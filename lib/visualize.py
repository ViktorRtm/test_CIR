import cairo
import mercantile
import math
import numpy as np
import imageio.v3 as iio


from pathlib import Path


def create_gif(args, surface, data_for_visual:dict[list[int]], addresses_data:dict):
    """
    Мisualizes the data on a map with the specified period and creates a GIF image with a heatmap.
    
    :param args: runtime args from opts.py
    :param surface: surface from image of map
    :param data_for_visual: data summed over a given period
    :type data_for_visual: dict[list[int]]
    :param addresses_data: Data of cameras
    :type addresses_data: dict
    """
    images = []
    data_keys = [key for key in data_for_visual]
    data_lenght = len(data_for_visual[data_keys[0]])
    map_coordinates = args.map_coordinates
    colors = args.colors


    for idx in range(data_lenght):
        
        height = surface.get_height()
        width = surface.get_width()
        context = cairo.Context(surface)
        time_sum_min = idx*15
        time_hour = time_sum_min // 60
        time_min = time_sum_min % 60
        time_text_hour = f'0{time_hour}' if time_hour < 10 else f'{time_hour}'
        time_text_min = f'0{time_min}' if time_min < 10 else f'{time_min}'
        time_text = f'{time_text_hour}:{time_text_min}'
        west, south, east, north, zoom = map_coordinates

        tiles = list(mercantile.tiles(west, south, east, north, zoom))
        west = min([mercantile.bounds(t).west for t in tiles])
        east = max([mercantile.bounds(t).east for t in tiles])
        south = min([mercantile.bounds(t).south for t in tiles])
        north = max([mercantile.bounds(t).north for t in tiles])

        leftTop = mercantile.xy(west, north)
        rightBottom = mercantile.xy(east, south)

        kx = width / (rightBottom[0] - leftTop[0])
        ky = height / (rightBottom[1] - leftTop[1])
        
        for key in data_keys:
            
            alredy = False
            automobile_count = data_for_visual[key][idx]

            for k in colors:
                if automobile_count < k and not alredy:
                    color = colors[k]
                    alredy = True
            
            c = addresses_data[key]['coordinates']
            x, y = mercantile.xy(c[0], c[1])
            x = (x - leftTop[0]) * kx
            y = (y - leftTop[1]) * ky

            for i in range(3):
                context.arc(x, y, 5+5*i, 0, 2 * math.pi)
                context.set_source_rgba(color[0], color[1], color[2], 0.3)  # красный, полупрозрачный
                context.set_line_width(10)  # ширина 10 пикселей
                context.fill()

            context.set_source_rgb(0, 0, 0)
            context.set_font_size(25) # Font size in user units (e.g., 0.5 units high)
            context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            context.move_to(5.0, 30.0)
            context.show_text(time_text)

        
        img_data = np.frombuffer(surface.get_data(), np.uint8)
        img_data = img_data.reshape(height, width, 4)[:, :, :3][:, :, ::-1]
        images.append(img_data)
        

    output_gif_filename = Path(args.gif_path + args.gif_name)
    iio.imwrite(output_gif_filename, images, duration=188, loop=0)