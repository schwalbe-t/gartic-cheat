
# Requires installed:
# - pynput
# - tkinter

import math
import sys
import time
import requests
import os
from PIL import Image
from io import BytesIO
import tkinter as tk
from pynput.mouse import Controller, Button

# RAISE THIS NUMBER TO MAKE DRAWING SLOWER
# LOWER IT TO MAKE IT FASTER
# (Some browsers might not be able to deal with lower numbers)
DRAW_SPEED = 0.006

def read_image(src):
    if src.startswith(("http://", "https://")):
        response = requests.get(src)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    elif os.path.exists(src):
        return Image.open(src).convert("RGB")
    else:
        raise ValueError("Invalid image source: Not a valid URL or file path")

if len(sys.argv) < 2:
    print("Usage: python main.py <image path/url>")
    sys.exit(1)

image = read_image(sys.argv[1])
img_width, img_height = image.size
img_ar = img_width / img_height

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()
dest_screen_fract = 0.45
dest_step_size = 5
dest_max_width = int(dest_screen_fract * screen_width)
dest_max_height = int(dest_screen_fract * screen_height)
dest_box_ar = dest_max_width / dest_max_height
dest_width = 0
dest_height = 0
if img_ar > dest_box_ar: # image is wider than destination box
    dest_width = dest_max_width
    dest_height = int(img_height * dest_max_width / img_width)
else: # image is taller than destination box
    dest_width = int(img_width * dest_max_height / img_height)
    dest_height = dest_max_height

print("Printing at cursor after 5 seconds...")
time.sleep(5)

mouse = Controller()
palette_root_x, palette_root_y = mouse.position
dest_root_x = palette_root_x + 180
dest_root_y = palette_root_y - 80

palette = [
    ((  0,   0,   0), (  0,   0)),
    ((102, 102, 102), ( 50,   0)),
    ((  0,  80, 205), (100,   0)),
    ((255, 255, 255), (  0,  50)),
    ((170, 170, 170), ( 50,  50)),
    (( 38, 201, 255), (100,  50)),
    ((  1, 116,  32), (  0, 100)),
    ((153,   0,   0), ( 50, 100)),
    ((150,  65,  18), (100, 100)),
    (( 17, 176,  60), (  0, 150)),
    ((255,   0,  19), ( 50, 150)),
    ((255, 120,  41), (100, 150)),
    ((176, 112,  28), (  0, 200)),
    ((153,   0,  78), ( 50, 200)),
    ((203,  90,  87), (100, 200)),
    ((255, 193,  38), (  0, 250)),
    ((255,   0, 143), ( 50, 250)),
    ((254, 175, 168), (100, 250))
]

def euclidean_distance(a, b):
    r1, g1, b1 = a[:3]
    r2, g2, b2 = b[:3]
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

def closest_color(target):
    closest_distance = float('inf')
    closest_coord = None
    for entry in palette:
        distance = euclidean_distance(target, entry[0])
        if distance < closest_distance:
            closest_distance = distance
            closest_coord = entry[1]
    return closest_coord

color_points = {}

for x in range(0, dest_width, dest_step_size):
    for y in range(0, dest_height, dest_step_size):
        img_x = x * img_width / dest_width
        img_y = y * img_height / dest_height
        color_x, color_y = closest_color(image.getpixel((img_x, img_y)))
        color_points.setdefault((color_x, color_y), []).append((x, y))

for (color_x, color_y), points in color_points.items():
    mouse.position = (palette_root_x + color_x, palette_root_y + color_y)
    mouse.click(Button.left)
    time.sleep(1.0)
    for (x, y) in points:        
        mouse.position = (dest_root_x + x, dest_root_y + y)
        mouse.click(Button.left)
        time.sleep(DRAW_SPEED)

print("Done!")