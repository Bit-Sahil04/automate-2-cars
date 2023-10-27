import cv2
import numpy as np
from PIL import Image, ImageDraw

# Define or import the undefined names
lane_width = 100
lane_divider_width = (0, 2, 5, 7)
game_offset_x = 9
detection_line_y = 746 - 400 - 120 - 150  # car_top_point - detection_offset
screenshot = None  # Initialize screenshot
screenshow = None  # Initialize screenshow

def get_circles(screenshot, region):
    x,y, w,h = region
    img = np.array(screenshot)
    img = img[  y: y+h, x: x+ w]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30, param1=50, param2=30, minRadius=5, maxRadius=150)
    if circles is not None and len(circles)!=0:
        return True
    return False

def get_squares(screenshot, region):
    x,y, w,h = region
    img = np.array(screenshot) 
    img = img[  y: y+h, x: x+ w]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            return True
    return False

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

    # Check if screenshot is initialized
    if screenshot is not None:
        color_top_left = screenshot.getpixel(top_left)
        color_center = screenshot.getpixel(center)
    else:
        print("Screenshot is not initialized.")
        return

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
    
    region=(
            (game_offset_x + lane_divider_width[lane_number])   + lane_width * lane_number, 
            car_top_point - 250, 
            lane_width, 
            100
        )
    # Check if draw is initialized
    if draw is not None:
        draw.rectangle(region, outline=(255, 255, 255))
    else:
        print("Draw is not initialized.")
        return

    # Check if screenshow is initialized
    if screenshow is not None:
        screenshow.show()
    else:
        print("Screenshow is not initialized.")
        return

    print(region, lane_number)

    region = (
            game_offset_x+lane_divider_width[lane_number] + lane_width * lane_number, 
            car_top_point-250, 
            lane_width, 
            100
            )

    # Check if get_circles and get_squares are defined
    try:
        is_circle = get_circles(screenshot, region)
        is_square = get_squares(screenshot, region)
    except NameError:
        print("get_circles and/or get_squares are not defined.")
        return

        return 'r'

    if is_circle:
        return f"{lane_number} c"
    
    if is_square:
        return f"{lane_number} s"
   
    return '\t'
