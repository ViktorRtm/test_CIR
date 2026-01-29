import argparse


parser = argparse.ArgumentParser(description='YOLOv12 based alg for automobile counting')

# ========================= Models Configs ==========================
parser.add_argument('--models_dir', type=str, default='models/', metavar='PATH')
parser.add_argument('--model_name', type=str, default='yolo12m.pt')
parser.add_argument('--conf', type=float, default=0.75)
parser.add_argument('--device', type=str, default='cuda')


# ========================= Learning Configs ==========================

# ========================= Display Configs ==========================

# ========================= Runtime Configs ==========================
parser.add_argument('--data_visualize_period', type=int, default=15)
parser.add_argument('--addresses_file_path', type=str, default='addresses.yaml', metavar='PATH')
parser.add_argument('--videos_storage_dir', type=str, default='/media/vitkor/project_dat/tests_work/CIR/videos/', metavar='PATH')
parser.add_argument('--videos_date', type=str, default='22.01.2026')
parser.add_argument('--map_path', type=str, default='maps/map.png', metavar='PATH')
parser.add_argument('--map_coordinates', type=list, default=[60.61432, 56.89003, 60.64281, 56.9041, 15], metavar='format - [west, south, east, north, zoom]')
parser.add_argument('--colors', type=dict, default={200: (0, 1, 0), 400: (1, 1, 0), 600: (1, 0, 0), 800: (0.545, 0, 0)}, metavar='Colors for heatmap')
parser.add_argument('--gif_name', type=str, default='22_01_2026.gif')
parser.add_argument('--gif_path', type=str, default='results/', metavar='PATH')

