The algorithm solves the following tasks:
 - counts the number of outomobile which cros crossroads

# Befor using
!!! FOR STARTING YOU MUST HAVE VIDEOCARD WITH CUDA!!! 
install required libraries
```shell
pip install requirements.txt
```

## Start parameters
When you start scripts, you should use the following parameters:
 - video_path - path to the video file to be analyzed
 - save_video - ```True/Flase```, and if ```True``` use save_video_dir
 - save_video_dir - path to the directory where save processed video
 - save_file_results - ```True/Flase```, and if ```True``` use save_file_results_dir
 - save_file_results_dir - path to the directory where save csv files with timecode of fact

You can use bash commandand, for example:
```shell
python3 main.py --video_path video/file/directory/AV2_164001_170001_T8C0_164001.mp4 --save_video False --save_file_results True --save_file_results_dir results
```
also you can use different tasks with bash command above(default values ​​are set ```True```):
```shell
python3 main.py --pay_detection False --seatbelt_detection True --phone_detection True --eat_drink_detection False
```

or change this parameters in file opts.py and start main.py
```shell
python3 main.py
```