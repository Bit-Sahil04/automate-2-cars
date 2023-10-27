# No changes needed in this snippet
import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
from PIL import Image, ImageDraw

import mss
import mss.tools

window = gw.getWindowsWithTitle('CPH2381')


window_x = 1492


if window:
    window[0].moveTo(window_x, 0)
else:
    print("Window not found!")



palette = {
    "red": (244, 56, 101),
    "blue": (0, 169, 192),
    "white": (255, 255, 255),
    "background": (37, 50, 123),
    "lane": (92, 110, 193),
    "dark_bg": (15, 19, 49)
}

# 54, 161, 269, 372
game_header_offset = 400
game_footer_offset = 120
car_lane_width = 107 
start_pos = 54


car_top_point = 746 - game_header_offset - game_footer_offset
car_mid_point = 787 - game_header_offset - game_footer_offset
car_bottom_point = 825 - game_header_offset - game_footer_offset
draw = None
screen = None
# 48 x 48 
[
    [(54, 746), (54, 787), (54, 825)]
]

car_pos = [False,True,True,False]
def color_diff(c1,c2):
    r1,b1,g1 = c1
    r2,b2,g2 = c2
    return (r1-r2)**2 + (b1-b2)**2 + (g1-g2)**2


def is_car_on_lane(lane_number: int):

    return car_pos[lane_number]

    car_heights = (car_top_point + game_footer_offset, car_mid_point + game_footer_offset, car_bottom_point + game_footer_offset) 
    car_x = start_pos + (car_lane_width * lane_number) 
    red = palette['red']
    blue = palette['blue']

    for i in range(3):
        # color = screen[car_x, car_heights[i]]
        color = screenshot.pixel(car_x, car_heights[i]) 

        if lane_number in (0, 1):
            
            if color != red:
                return False
        
        else:
            if color != blue:
                return False

    return True



def get_circles(pil_image, region):
    
    x,y, w,h = region
    img = np.array(pil_image)
    
    # img = img[ x: x+ w, y: y+h , :]
    img = img[  y: y+h, x: x+ w]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30, param1=50, param2=30, minRadius=5, maxRadius=150)
    
    if circles is not None and len(circles)!=0:
        return True
    
    return False


def get_squares(pil_image, region):
    
    x,y, w,h = region

    img = np.array(pil_image) 
    # img = img[ x: x+ w, y: y+h ]

    img = img[  y: y+h, x: x+ w]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur the image to reduce noise
    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges
    edges = cv2.Canny(gray, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Approximate contour to a polygon
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the polygon has 4 vertices (could be square or rectangle)
        if len(approx) == 4:
            # Draw the contour on the original image
            # cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
            return True
    
    return False


detection_offset = 150 # 150
detection_line_y = car_top_point - detection_offset

x_mids =  [60 , 164 , 269 , 374 ] 
lane_divider_width = (0, 2, 5, 7)
lane_width = 100
game_offset_x = 9


def count_pixel_on_line(lane_number, height):
    
    x_start = game_offset_x + lane_divider_width[lane_number]  + lane_width * lane_number
    x_end = x_start + lane_width

    pixels = 0
    background = palette['background']
    red = palette['red']
    blue = palette['blue']
    white = palette['white']

    x_mid  = x_start + (x_end - x_start)//2
    # current_pixel = screen[x_mid, height]
    current_pixel = screenshot.pixel(x_mid, height) 
    if color_diff(current_pixel, background) < 20000:
        return 0
    
    # start = x_mid
    # while start > x_start:

    #     current_pixel = screenshot.pixel(i, height)
        
    #     if color_diff(current_pixel, background) > 2000:
    #         # print(current_pixel)
    #         pixels += 1
    #     else:
    #         break
        
    #     start -= 1
    
    # start = x_mid

    # while start < x_end:

    #     # current_pixel = screen[start, height]
    #     current_pixel = screenshot.pixel(i, height)
        
    #     if color_diff(current_pixel, background) > 2000:
    #         pixels += 1
    #     else:
    #         break
        
    #     start += 1
    # print(x_start, x_end+1)
    for i in range(x_start, x_end+1):
        # current_pixel = screen[i, height]
        current_pixel = screenshot.pixel(i, height)
        # current_pixel = screenshot.getpixel((i, height))
        # print(current_pixel, background, color_diff(current_pixel, background)  )
        if color_diff(current_pixel, background) > 30000:
            # print(current_pixel)
            pixels += 1
    #     # screenshot.putpixel((i, height), (255, 10, 250))

    return pixels 

total_pixels = 0


def get_object_on_lane_by_pixels(lane_number):
    global total_pixels

    c1 = count_pixel_on_line(lane_number, detection_line_y + 13)
    c2 = count_pixel_on_line(lane_number, detection_line_y - 13)
    # c3 = count_pixel_on_line(lane_number, detection_line_y - 27)
    
    thresholds = [50, 50, 25, 50]
    threshold = 50
    # print(lane_number, c1, c2, c1 + c2)

    # if not (c1 and c2 and c3):
        # return 'n'
    total_pixels = c1 + c2  # + c3
    
    if total_pixels < 5:
        return 'n'
    
    print(total_pixels, end = " ")
    print("c" if total_pixels < threshold else "s")
    if total_pixels > threshold:
        return 's'
    
    return 'c' 


def tap_screen(lane_number):

    if lane_number <2:
        car_pos[0],car_pos[1] = car_pos[1],car_pos[0]
    
    else:
        car_pos[2],car_pos[3] = car_pos[3],car_pos[2]

    tap_x = lane_width * lane_number + lane_width // 2
    tap_y = car_mid_point
    screen_offset_x = 1492
    screen_offset_y = car_bottom_point + game_footer_offset
    
    pyautogui.click(screen_offset_x + tap_x, 200)
    print(f"{lane_number}  ", total_pixels)

    print(car_pos)


def count_pixels_on_lane_y(lane_number, height):
    background = palette['background']
    dark_bg = palette['dark_bg']
    
    # x_start = game_offset_x + lane_divider_width[lane_number]  + lane_width * lane_number
    # x_end = x_start + lane_width

    # x_mid = (x_start + x_end)//2
    
    x_mid = x_mids[lane_number]
    
    x_check = x_mid - 20 # square width
    
    current_pixel = screenshot.pixel(x_check, height)
    color_threshold = 5000

    # save_disk(screenshot, draw=[(x_check, height)], count=2)
    # raise

    is_background = lambda x: color_diff(x, background) < color_threshold or color_diff(x, dark_bg) < color_threshold


    if is_background(current_pixel):
        return 0

    total_pixels = 0

    y_check = height
    
    # colors = []

    while not is_background(current_pixel):
        total_pixels += 1
        current_pixel = screenshot.pixel(x_check, y_check)
        y_check -=1
        # colors.append((current_pixel,color_diff(current_pixel, background), 0) )
        # colors.append((x_check, y_check))
    
    y_check = height
    current_pixel = screenshot.pixel(x_check, height)
    
    while not is_background(current_pixel):
        total_pixels += 1
        current_pixel = screenshot.pixel(x_check, y_check)
        y_check +=1
        # colors.append((current_pixel,color_diff(current_pixel, background), 1) )
        # colors.append((x_check, y_check))

    
    # if 5 < total_pixels < 15:
        # print(colors)
        # save_disk(screenshot, draw=colors, count=2)
        # raise
    
    print("total pixels ", total_pixels)
    
    return total_pixels


    # 51 



def get_shape_on_lane(lane_number):
    global score, score_updates
    
    c1 = count_pixel_on_line(lane_number, detection_line_y)
    shape = 'n'

    if c1  == 0 and score[lane_number] != 0:        
        # count +=1 
        
        avg = score[lane_number] / score_updates[lane_number]

        shape = 's' if avg >= 39.5 else 'c'

        # print(count, score[0], shape, avg )
        
        score[lane_number] = 0
        score_updates[lane_number] = 0
        # screenshot.save(output=f"modified_screenshot_{count}.png")
        # save_disk(screenshot, count)
    else:
        score[lane_number] += c1
        if c1 != 0:
            score_updates[lane_number] += 1
            # time.sleep(0.03)

    if shape != 'n':
        print(lane_number, "  ", shape)
        
    return shape


def detect_shape_on_lane(lane_number):
    
    x_start = window_x +  game_offset_x + lane_divider_width[lane_number]  + lane_width * lane_number
    height = 130

    region = (
        x_start, 527, lane_width, height
    )
    # region=(1502,527,98,74)

    circle = pyautogui.locateCenterOnScreen('circle_blue.png', confidence=0.8, grayscale=True, region=region)
    square = pyautogui.locateCenterOnScreen('square_blue.png', confidence=0.8, grayscale=True, region=region)

    if circle:
        return 'c'
    
    if square:
        return 's'
    
    return 'n'


def get_object_on_lane_by_pixels_y(lane_number):
    c1 = count_pixels_on_lane_y(lane_number, detection_line_y)

    # previous_score = lane_scores[lane_number]
    # tolerance = 4
    # difference =  abs(previous_score - c1)
    
    # lane_scores[lane_number] = c1

    circle_threshold = lane_thresholds[lane_number]  # 35

    # if difference < tolerance:
    #     return 'n'

    if c1 >= circle_threshold:
        return 's'
    
    elif 5 < c1 < circle_threshold:
        return 'c'
    
    return 'n'
    

    



def take_action(lane_number):
    obj = get_object_on_lane_by_pixels_y(lane_number)
    is_car = is_car_on_lane(lane_number)

    if obj == 'n':
        return

    if obj == 's' and is_car:
        tap_screen(lane_number)
        print(f'Tapped {lane_number} for square')
    
    if obj == 'c' and not is_car:
        tap_screen(lane_number)
        print(f'Tapped {lane_number} for circle')
    return


import time

count = 0 
frames = 0


# score = [0, 0, 0, 0]
# score_updates = [0, 0, 0, 0]
lane_scores = [0, 0, 0, 0]

lane_thresholds = [ 35, 37, 33, 38 ]




def save_disk(image, count=0, draw=None):
    img = Image.frombytes("RGB", image.size, image.bgra, "raw", "BGRX")


    if draw is None:
        draw = []
    
    for coord in draw:
        x, y = coord
        img.putpixel((x, y), (255, 0, 0))


    # Save the PIL Image
    img.save(f'modified_screenshot_{count}.png')

with mss.mss() as sct:
    # The screen part to capture
    region = {'top': game_header_offset, 'left': 1492, 'width': 430, 'height': 964 - game_header_offset - game_footer_offset}

    # Grab the data
    img = sct.grab(region)

    while True:
        frames += 1
        start = time.time()
        # screenshot = pyautogui.screenshot(region=(1492, game_header_offset, 430, 964 - game_header_offset - game_footer_offset))
        
        screenshot = sct.grab(region)
        # screen = screenshot.load()
        # screenshot.save(output=f"modified_screenshot_{count}.png")
        # save_disk(screenshot)
        # break
        # shape_0 = get_shape_on_lane(0)

        # screenshot = np.array(screenshot)
        # No changes needed in this snippet
        # print(is_car_on_lane(0), end=' ')
        # print(is_car_on_lane(1), end=" ")
        # print(is_car_on_lane(2), end=" ")
        # print(is_car_on_lane(3))

        # print(get_object_type_on_lane(0), end=' ')
        # print(get_object_type_on_lane(1), end=" ")
        # print(get_object_type_on_lane(2), end=" ")
        # print(get_object_type_on_lane(3))
        # break

        # c1, c2, c3 = get_object_on_lane_by_pixels(0) 

        # if c1 != 0 and c2 != 0 and c3 != 0:
        #     screenshot.save(f"modified_screenshot_{count}.png")
        #     count +=1
        #     print(count -1, c1, c2, c3)
        
        # obj1 = get_object_on_lane_by_pixels(0)
        # obj2 = get_object_on_lane_by_pixels(1)
        # obj4 = get_object_on_lane_by_pixels(3)


        # obj3 = get_object_on_lane_by_pixels_y(0) # 28, 39
        # obj3 = get_object_on_lane_by_pixels_y(1) # # 32, 42
        # obj3 = get_object_on_lane_by_pixels_y(2) # 27, 38
        # obj3 = get_object_on_lane_by_pixels_y(3) # 33, 43
        take_action(1)
        take_action(0)
        take_action(2)
        take_action(3)
        # s = detect_shape_on_lane(1)
        # if s != 'n':
        #     print(s)
        # get_shape_on_lane(0)
        # get_shape_on_lane(1)
        # get_shape_on_lane(2)
        # get_shape_on_lane(3)
        # No changes needed in this snippet
        # take_action(0)
        # take_action(1)
        # if obj != 'n':
        #     print(count, obj)
        # screenshot.save(f"modified_screenshot_{count}.png")
        #     count +=1
        # break

        delta = time.time() - start
        if frames%100 == 0:
            print(delta)
























# No changes needed in this snippet
# def get_object_type_on_lane(lane_number):

#     center_x =  (lane_number + 1) * lane_width  + (lane_divider_width[lane_number]) 
#     center_x = (center_x - lane_width//2) + game_offset_x

#     top_left = (center_x - 19, detection_line_y - 19)
#     center  = (center_x , detection_line_y)


     
    # color_top_left = screenshot.getpixel(top_left)
    # color_center = screenshot.getpixel(center)

    # background = palette['background']
    # red = palette['red']
    # blue = palette['blue']

    # region=(
    #         (game_offset_x + lane_divider_width[lane_number])   + lane_width * lane_number, 
    #         car_top_point - 250, 
    #         lane_width, 
    #         100
    #     )
    # draw.rectangle(region, outline=(255, 255, 255))
    # screenshow.show()

    # print(region, lane_number)

    # region = (
    #     game_offset_x+lane_divider_width[lane_number]) + lane_width * lane_number, 
    #     car_top_point-250, 
    #     lane_width, 
    #     100
    #     )

    # is_circle = get_circles(screenshot, region)
    # is_square = get_squares(screenshot, region)


    # print(color_top_left, color_center)
    
    # if color_top_left == color_center == palette['background']:
    #     screenshot.putpixel(top_left, (255, 10, 250))
    #     screenshot.putpixel(center, (255, 10, 250))

    #     # Save the modified screenshot
    #     screenshot.save('modified_screenshot.png')
        
    #     return 'n'  // (lane_width + 1) * lane_number
    # if color_top_left == background and (color_center  in (red, blue)):
        
        # screenshot.putpixel(top_left, (255, 10, 250))
        # screenshot.putpixel(center, (255, 10, 250))

        # Save the modified screenshot
        # screenshot.save('modified_screenshot.png')
    
    #     return 'c'
    
    # if color_top_left == color_center and (color_center in (red, blue)):

    #     # screenshot.putpixel(top_left, (255, 10, 250))
    #     # screenshot.putpixel(center, (255, 10, 250))

    #     # # Save the modified screenshot
    #     # screenshot.save('modified_screenshot.png')

    #     return 'r'

    # if is_circle:
    #     return f"{lane_number} c"
    
    # if is_square:
    #     return f"{lane_number} s"
   
    # return '\t'

# with Image.open("modified_screenshot.png") as screenshot:
    
#     draw = ImageDraw.Draw(screenshot)


#     print(get_object_type_on_lane(0), end=' ')
#     print(get_object_type_on_lane(1), end=" ")
#     print(get_object_type_on_lane(2), end=" ")
#     print(get_object_type_on_lane(3))

#==================================







    # search_region=(
    #     (
    #         lane_divider_width[lane_number])  + 1492  + lane_width * lane_number, 
    #         car_top_point - 250, 
    #         lane_width, 
    #         100
    #     )
    
    # # region =  (  1492,    )

    # red_circle = pyautogui.locateOnScreen('circle_blue.png',)
    # red_square = pyautogui.locateOnScreen('circle_red.png', )
    # blue_circle = pyautogui.locateOnScreen('square_blue.png')
