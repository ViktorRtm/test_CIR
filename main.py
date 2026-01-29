import torch
import yaml
import cairo
import sys

sys.path.append(r'lib/')

from pathlib import Path
from ultralytics import YOLO
from lib.utils import cpu_info, gpu_info
from lib.counter import AutomobileCounter
from lib.opts import parser
from lib.processing import postprocessing
from lib.visualize import create_gif


def main(args):

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    if device == 'cpu':
        args.device = device
        print(f'Running on device: {cpu_info()}')
    else:
        args.device = device
        print(f'Running on device: {gpu_info()}')

    try:
        model_path = Path(args.models_dir + args.model_name)
        model = YOLO(model_path)
        print('[INFO] Complete creating model.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        model = None
        print(f'[WARN] Model not init. Alg would stoped.')
        return
    
    try:
        with open(args.addresses_file_path, 'r') as f:
            addresses_data = yaml.safe_load(f)
        print(f'[INFO] Addresses data for video processing success LOAD.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        print(f'[WARN] Addresses data for video processing not LOAD. Alg would stoped.')
        return
    
    counter = AutomobileCounter(args, model, device, addresses_data)

    for video_dir_name in addresses_data.keys():
        automobile_counter = [0]
        video_folder = Path(args.videos_storage_dir + str(video_dir_name))
        if video_folder.is_dir():
            counter.video_analize(video_dir_name=video_dir_name, videos_folder=video_folder, automobile_counter=automobile_counter)
    
    try:
        with open('/home/vitkor/projects/tests_work/addresses.yaml', 'w') as f:
            yaml.dump(counter.addresses_data, f, default_flow_style=False, sort_keys=False)
        print(f'[INFO] Addresses data after video processing success SAVE.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        print(f'[WARN] Addresses data not SAVE. Try save data from log. Alg would stoped.')
        print(f'[WARN] {counter.addresses_data}')
        return
    
    try:
        with open(args.addresses_file_path, 'r') as f:
            addresses_data = yaml.safe_load(f)
        print(f'[INFO] Addresses data for vizulize results success LOAD.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        print(f'[WARN] Addresses data for vizulize results not LOAD. Alg would stoped.')
        return
    try:
        data_for_visual = postprocessing(addresses_data=addresses_data, period=args.data_visualize_period, date=args.videos_date)
        print(f'[INFO] Postprocessing for visualize data finished success.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        print(f'[WARN] Postprocessing for visualize data finished with ERROR. Alg would stoped.')
        return
    
    try:
        surface = cairo.ImageSurface.create_from_png(args.map_path)
        print(f'[INFO] Create map surface complite success.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        print(f'[WARN] Create map surface complite with ERROR. Alg would stoped.')
        return

    try:
        create_gif(args, surface, data_for_visual, addresses_data)
        print(f'[INFO] Create gif with heatmap complite success.')
    except Exception as ex:
        print(f'[WARN] {ex}')
        print(f'[WARN] Create gif with heatmap complite with ERROR. Alg would stoped.')
        return    

    
if __name__ == '__main__':
    
    args = parser.parse_args()

    main(args)