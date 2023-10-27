import cv2
import numpy as np
from PIL import Image, ImageDraw

palette = {
    "red": (244, 56, 101),
    "blue": (0, 169, 192),
    "white": (255, 255, 255),
    "background": (37, 50, 123),
    "lane": (92, 110, 193),
    "dark_bg": (15, 19, 49)
}

game_header_offset = 400
game_footer_offset = 120
car_lane_width = 107 
start_pos = 54

car_top_point = 746 - game_header_offset - game_footer_offset
car_mid_point = 787 - game_header_offset - game_footer_offset
car_bottom_point = 825 - game_header_offset - game_footer_offset
draw = None
screen = None

car_pos = [False,True,True,False]

def color_diff(c1,c2):
    r1,b1,g1 = c1
    r2,b2,g2 = c2
    return (r1-r2)**2 + (b1-b2)**2 + (g1-g2)**2

def get_object_type_on_lane(lane_number):
    center_x =  (lane_number + 1) * lane_width  + (lane_divider_width[lane_number]) 
    center_x = (center_x - lane_width//2) + game_offset_x

    top_left = (center_x - 19, detection_line_y - 19)
    center  = (center_x , detection_line_y)

    color_top_left = screenshot.getpixel(top_left)
    color_center = screenshot.getpixel(center)

    background = palette['background']
    red = palette['red']
    blue = palette['blue']

    region=(
            (game_offset_x + lane_divider_width[lane_number])   + lane_width * lane_number, 
            car_top_point - 250, 
            lane_width, 
            100
        )
    draw.rectangle(region, outline=(255, 255, 255))
    screenshow.show()

    print(region, lane_number)

    region = (
            game_offset_x+lane_divider_width[lane_number] + lane_width * lane_number, 
            car_top_point-250, 
            lane_width, 
            100
            )

    is_circle = get_circles(screenshot, region)
    is_square = get_squares(screenshot, region)

    print(color_top_left, color_center)
    
    if color_top_left == color_center == palette['background']:
        screenshot.putpixel(top_left, (255, 10, 250))
        screenshot.putpixel(center, (255, 10, 250))

        # Save the modified screenshot
        screenshot.save('modified_screenshot.png')
        
        return 'n'  # (lane_width + 1) * lane_number
    if color_top_left == background and (color_center  in (red, blue)):
        
        screenshot.putpixel(top_left, (255, 10, 250))
        screenshot.putpixel(center, (255, 10, 250))

        # Save the modified screenshot
        screenshot.save('modified_screenshot.png')
    
        return 'c'
    
    if color_top_left == color_center and (color_center in (red, blue)):

        # screenshot.putpixel(top_left, (255, 10, 250))
        # screenshot.putpixel(center, (255, 10, 250))

        # # Save the modified screenshot
        # screenshot.save('modified_screenshot.png')

        return 'r'

    if is_circle:
        return f"{lane_number} c"
    
    if is_square:
        return f"{lane_number} s"
   
    return '\t'
