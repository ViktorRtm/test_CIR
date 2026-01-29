import cv2
import utils
import copy

from opts import parser
from ultralytics import YOLO


class AutomobileCounter():
    def __init__(
            self,
            args,
            model,
            device:str,
            addresses_data: dict
    ):
        self.args = args
        self.model = model
        self.device = device
        self.addresses_data = addresses_data
        self.DATE = self.args.videos_date

        self.curr_max = 0
        self.last_max = 0
        self.INTERVAL = 60 * 1000

    def video_analize(self, video_dir_name:str, videos_folder, automobile_counter:list[int]):
        """
        Count automobile which cros crossroads every 1 minute.
        
        :param video_dir_name: camera id from addresses data.
        :type video_dir_name: str
        :param videos_folder: directory with videos from camera on 1 day.
        :param automobile_counter: list form save count of automobile.
        :type automobile_counter: list[int]
        """

        
        for video_file in sorted(videos_folder.iterdir()):
            
            next_time = 60 * 1000

            cap = cv2.VideoCapture(filename=video_file)

            assert cap.isOpened(), 'Error reading video file'
            w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
            video_roi = self.addresses_data[video_dir_name]['roi']
            video_roi = [
                int(video_roi[0]*w),
                int(video_roi[1]*h),
                int(video_roi[2]*w),
                int(video_roi[3]*h),
                ]
            print(f'[INFO] Start analize video - {video_file.name}.')

            while cap.isOpened():

                success, frame = cap.read()
                time_from_video_start = int(cap.get((cv2.CAP_PROP_POS_MSEC)))
                if not success:
                    break
                

                croped_frame = utils.crop_frame(
                    frame=frame,
                    crop_area=video_roi,
                    verbose=False
                )

                results = self.model.track(
                    source=croped_frame,
                    classes=[2],
                    conf=self.args.conf,
                    device=self.device,
                    persist=True,
                    verbose=False
                )

                if results[0].boxes.id != None:  
                    indexes = results[0].boxes.id.int().tolist()
                    max_idx = int(max(indexes))
                    if max_idx > self.curr_max:
                        self.curr_max = copy.copy(max_idx)
                        
                if (time_from_video_start != 0) and (time_from_video_start>next_time):
                    next_time += self.INTERVAL
                    automobile_counter.append(self.curr_max-self.last_max)
                    self.last_max = copy.copy(self.curr_max)
            print(f'[INFO] Analize video - {video_file.name}, finished.')
        res = {self.DATE: automobile_counter}
        self.addresses_data[video_dir_name]['results'] = res