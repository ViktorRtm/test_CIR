import os
import cpuinfo
import GPUtil
import cv2
import io
import json
import numpy as np
import math
import torch

from torchvision import ops
from cProfile import Profile
from pstats import SortKey, Stats
from config import print


def cpu_info() -> dict:
    if info := cpuinfo.get_cpu_info():
        cpu_info = {
            "Name": info['brand_raw'],
            "Manufacturer": info['vendor_id_raw'],
            "Architecture": info['arch_string_raw'],
            "NumberOfLogicalProcessors": info['count'],
            "NumberOfPhysicalProcessors": int(int(info['count']) / 2),
            "CurrentRefreshRate": info['hz_actual_friendly'],
            "L2CacheSize": info['l2_cache_size'],
            "L3CacheSize": info['l3_cache_size']
        }
        return cpu_info if cpu_info else False
    return False


def gpu_info() -> dict:
    gpus_list = dict()
    if gpus := GPUtil.getGPUs():
        for gpu in gpus:
            gpus_list.update({
                "ID": gpu.id,
                "Name": gpu.name,
                "Load": f'{gpu.load * 100}%',
                "FreeMemory": gpu.memoryFree,
                "UsedMemory": gpu.memoryUsed,
                "TotalMemory": gpu.memoryTotal,
                "GPUTemp": f'{gpu.temperature} C'
            })
        return gpus_list if gpus_list else False
    return False


def save_faces(frame, faces, save_dir, current_counter=0, margin=10):
    '''Save pictures based on recognized objects' bounding boxes.'''
    for id, bbox in faces.items():
        # this_id_files = [item for item in os.listdir(save_dir) if item.startswith(id)]
        # current_counter = max([])
        filename = os.path.join(save_dir, f"{current_counter}.jpg")
        current_counter += 1
        cropped = frame[
            bbox[1] - margin : bbox[3] + margin, bbox[0] - margin : bbox[2] + margin, :
        ].copy()
        cv2.imwrite(filename, cropped)
    return current_counter


def resize_image(image, target_height=600, target_width=None):
    if target_width is not None:
        new_dim = (target_width, target_height)
    else:
        height, width, _ = image.shape
        scale_factor = target_height / height
        new_dim = (int(width * scale_factor), int(target_height))
    new_image = cv2.resize(image, new_dim)
    return new_image


def crop_frame(frame, crop_area, verbose):
    '''Crop frame based on set coordinates.'''
    try:
        frame = frame[
            crop_area[1] : crop_area[3], crop_area[0] : crop_area[2], :
        ]
    except Exception:
        if verbose:
            print("Crop area not set, working with original frame")
            try:
                print(crop_area, frame.shape)
            except Exception:
                pass
    return frame


def calculate_iou(detect_bbox:list, bd_bbox:list) -> float:
    """
    return:
    iou: float - rounded to 2
    """
    try:
        detected_bbox_tensor = torch.tensor([detect_bbox])
        bd_bbox_tensor = torch.tensor([bd_bbox])
        iou = round(ops.box_iou(detected_bbox_tensor, bd_bbox_tensor).item(), 2)
    except Exception as ex:
        print(f'[WARN] IoU was not calculated:\t{ex}')
        iou = 0.0
    return iou


def check_direction(rect, check_area, direction='top'):
    assert direction in ['top', 'bottom', 'left', 'right']
    check_x1, check_y1, check_x2, check_y2 = list(check_area)
    # height, width = check_area.shape
    x1, y1, x2, y2 = rect
    rule = {
        'top': y1 <= check_y1 <= y2,
        'bottom': y1 <= check_y2 <= y2,
        'left': x1 <= check_x1 <= x2,
        'right': x1 <= check_x2 <= x2,
    }
    return rule[direction]


def show_progress_bar(percent_complete, prev_percent, step=10):
    if int(percent_complete) > int(prev_percent):
        if percent_complete % step == 0:
            text = f"[{'=' * int(percent_complete/4)}{' ' * (25 - int(percent_complete/4))}] {percent_complete:.0f}%"
            print(text)
            return percent_complete
    return None


def select_rois(frame):
    '''Select rectangle regions.'''
    scale_rate = 0.5
    frame = cv2.resize(
        frame, (0, 0), fx=scale_rate, fy=scale_rate
    )
    height, width, _ = frame.shape
    r = cv2.selectROIs(f"Select ROIs {frame.shape}", frame)
    d = dict()
    if isinstance(r, tuple):
        print("Zero ROIs selected.")
        return
    for index, roi in enumerate(r.tolist()):
        roi[2] += roi[0]
        roi[3] += roi[1]
        d[f"ROI_{index}"] = [
            round(roi[0] / width, 3),
            round(roi[1] / height, 3),
            round(roi[2] / width, 3),
            round(roi[3] / height, 3)
        ]
    return d


def click_event(event, x, y, flags, params):
    '''Add new point to list on left button click.'''
    if event == cv2.EVENT_LBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        height, width, _ = params[0]
        new_x = round(x / width, 3)
        new_y = round(y / height, 3)
        print(f'[{new_x}, {new_y}]', end=", ")
        params[1].append([new_x, new_y])
    if event == cv2.EVENT_RBUTTONDOWN:
        print("Use left button to select a point\nTo end selection don't select any point and directly press ENTER")


def select_points(frame):
    '''Select a list of points.'''
    scale_rate = 0.5
    # resize frame to see the whole picture
    resized_frame = cv2.resize(
        frame.copy(), (0, 0), fx=scale_rate, fy=scale_rate
    )
    print(f'Frame shape: {resized_frame.shape}')
    point_list = []
    params = [resized_frame.shape, point_list]
    cv2.imshow("resized_frame", resized_frame)
    cv2.setMouseCallback('resized_frame', click_event, params)
    cv2.waitKey(0)
    cv2.destroyWindow('resized_frame')
    return params[1]


def select_polygons(frame):
    '''Select a list of polygons.'''
    scale_rate = 0.5
    # resize frame to see the whole picture
    resized_frame = cv2.resize(
        frame.copy(), (0, 0), fx=scale_rate, fy=scale_rate
    )
    print(f'Frame shape: {resized_frame.shape}')
    polygons = {}
    while True:
        print('To compose a new polygon, select 4 points by pressing LEFT BUTTON, then press ENTER')
        print('To complete selection, directly press ENTER')
        point_list = []
        params = [resized_frame.shape, point_list]
        cv2.imshow("resized_frame", resized_frame)
        cv2.setMouseCallback('resized_frame', click_event, params)
        cv2.waitKey(0)
        cv2.destroyWindow('resized_frame')
        if len(params[1]) == 0:
            break
        roi_name = input("\nSet new roi name: ")
        polygons[roi_name] = point_list
    return polygons


def stack_images(image1, image2, hstack=True, target_height=600, show=False):
    '''Stack 2 images horizontally.'''
    if hstack:
        result = np.hstack([
            resize_image(image1, target_height=target_height),
            resize_image(image2, target_height=target_height)
        ])
        if show:
            height, width, _ = result.shape
            cv2.imshow(f'output {width}, {height}', result)
            cv2.waitKey()
            cv2.destroyAllWindows()
        else:
            return result


def hsv_to_bgr(source_color):
    '''
    h - hue [0..1]
    s - saturation [0..1]
    v - vibrance [0..1]
    '''
    h, s, v = source_color
    assert (
        h <= 1 and h >= 0
        and s <= 1 and s >= 0
        and v <= 1 and v >= 0
    ), "h, s, v values need to be between [0..1]"
    i = math.floor(h*6)
    f = h*6 - i
    p = v * (1-s)
    q = v * (1-f*s)
    t = v * (1-(1-f)*s)

    r, g, b = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i%6)]
    return (int(b * 255), int(g * 255), int(r * 255))


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class Profiler():
    def __init__(self, min_verbose=1, verbose=0):
        self.profiler = Profile()
        self.verbose = verbose
        self.min_verbose = min_verbose

    def start(self):
        if self.verbose > self.min_verbose:
            self.profiler.enable()
    
    def end(self):
        if self.verbose > self.min_verbose:
            try:
                self.profiler.disable()
                s = io.StringIO()
                ps = Stats(self.profiler, stream=s).sort_stats(SortKey.TIME)
                ps.print_stats(10)
                print(s.getvalue())
            except Exception:
                print('[WARN] could not get profiling results, make sure you initialized cProfile instance')
