The algorithm solves the following tasks:
 - counts the number of automobile which cros crossroads and visualize data on map.

# Befor using
!!! FOR STARTING YOU MUST HAVE VIDEOCARD WITH CUDA!!! 
install required libraries
```shell
pip install requirements.txt
```

Video dir structure:
'''shell
├── videos/
    ├── camera_id/
        ├── video_from_camera.mp4
    └── glaz.naroda.138-4238e06058/
        └── glaz.naroda.138-4238e06058_1769022000_86340_001.mp4
'''

## Start parameters
When you start scripts, you should use the following parameters:
 - addresses_file_path - path to file with data about video (id of camera, address of location, coordinates on map, roi for crop video, detection results on date)
 - videos_storage_dir - path to the videos storage dir.
 - videos_date - date when record video.
 - map_path - path to .png image with map.
 - map_coordinates - format [west, south, east, north, zoom].
 - data_visualize_period - the period in minutes for which the data will be displayed on one slide gif.
 - gif_path - dir path for save gif.
 - gif_name - file name for save gif.

You can use bash commandand, for example:
```shell
python3 main.py --video_storage_dir /media/vitkor/project_dat/tests_work/CIR/videos/ --video_date '22.01.2026' --map_path maps/map.png --map_coordinates [60.61432, 56.89003, 60.64281, 56.9041, 15]
```

or change this parameters in file opts.py and start main.py
```shell
python3 main.py
```