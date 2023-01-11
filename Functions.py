import os
import sys
import Box
import math
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt


def resize_image(img,scale_percent):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    interpolation = cv.INTER_AREA
    img = cv.resize(img, dim, interpolation)
    return img


def get_contour_max_area(contours):
    area=0
    max_area=0
    second_max=0
    count=0
    second_counter  =0
    for c in range(len(contours)):
        area=cv.contourArea(contours[c])
        if area>max_area:
            #print("area", area)
            second_counter=count
            second_max=max_area
            max_area=area
            count=c
            #print(count)
    max=[count,max_area,second_counter,second_max]
    return max


def crop_image(img, corners):
    square_points=make_suqare_from_corners(corners)
    min_x=square_points[0][0]
    min_y=square_points[0][1]
    max_x=square_points[3][0]
    max_y=square_points[3][1]

    cropped_img=img[min_y:max_y,min_x:max_x]
    coords = [min_y, max_y,min_x, max_x]
    return [coords, cropped_img]


def make_suqare_from_corners(square):
    smallest_x=square.item(0)
    smallest_y=square.item(1)
    max_x=square.item(0)
    max_y=square.item(1)
    for i in range(0,((len(square)*2)-1),2):
        x=square.item(i)
        y=square.item(i+1)
        if x< smallest_x:
            smallest_x=x
        if y< smallest_y:
            smallest_y=y
        if x>max_x:
            max_x=x
        if y>max_y:
            max_y=y

    p1 = [smallest_x, smallest_y]
    p2 = [max_x     , smallest_y]
    p3 = [smallest_x, max_y     ]
    p4 = [max_x     , max_y     ]

    square_points=[p1,p2,p3,p4]
    return  square_points


def seperate_box(img):
##    img = img[10:img.shape[0]-10, 10:img.shape[1]-10]

    height = img.shape[0]
    width = img.shape[1]
    box_h = math.floor(height/8)
    box_w = math.floor(width/8)

    boxes=[]
    y = 0
    x = 0
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    for i in range(8):
        row = img[y:y+box_h, :]
        y=y+box_h
        boxes.append([])
        for j in range(8):
            names = "" + chr(ord('a')+j) + str(8-i)
            box = row[:, x:x+box_w]
            box_ob = Box.Box(names, box) 
            boxes[i].append(box_ob)
            x=x+box_w
        x = 0
    return boxes


def crop_board(img):
    THRESHOLDING_window=15

    frame_BGR_original = img.copy()
    frame_BGR_resized = resize_image(frame_BGR_original, 20)

    frame_GRAY = cv.cvtColor(frame_BGR_resized, cv.COLOR_BGR2GRAY)
    
##    frame_GRAY_blured = cv.GaussianBlur(frame_GRAY, (15, 15), 0)
    frame_GRAY_blured = cv.medianBlur(frame_GRAY, 7)
    
    frame_THRESHOLDED = cv.adaptiveThreshold(frame_GRAY_blured, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
     cv.THRESH_BINARY_INV, THRESHOLDING_window, 2)
    
    contours, hierarchy = cv.findContours(frame_THRESHOLDED, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_NONE)
    largest_contour_index = get_contour_max_area(contours)[0]
    #print(largest_contour_index)

    if largest_contour_index == 0:
        print("Board Not Fount!")
        sys.exit()

    largest_contoured_polygon = cv.approxPolyDP(contours[largest_contour_index],
    0.05 * cv.arcLength(contours[largest_contour_index], True), True)
   
    coordinates, frame_BGR_cropped = crop_image(frame_BGR_resized, largest_contoured_polygon)
    return [coordinates, frame_BGR_cropped]


def crop_board_with_coordinates(img, coords):
    frame_BGR_original = img.copy()
    frame_BGR_resized = resize_image(frame_BGR_original, 20)
    frame_BGR_cropped = frame_BGR_resized[coords[0]:coords[1], coords[2]:coords[3]]
    return frame_BGR_cropped


def apply_threshold(img1_original, img2_original):
    # img1 = cv.equalizeHist(img1_original[:,:,0])
    # img2 = cv.equalizeHist(img2_original[:,:,0])

    img1 = cv.GaussianBlur(img1_original, (15,15), 0)
    img2 = cv.GaussianBlur(img2_original, (15,15), 0)

    image_diff = cv.absdiff(img1,img2)
    image_diff_gray = cv.cvtColor(image_diff, cv.COLOR_BGR2GRAY)

    matrix,thresold = cv.threshold(image_diff_gray, 30, 255, cv.THRESH_BINARY)
    thresold = cv.GaussianBlur(thresold, (15,15), 0)
    return thresold


def plot_tiles(boxes):
    for i in range(8):
        for j in range(8):
            plt.subplot(8, 8, j+1+(i*8)), plt.imshow(boxes[i][j].image)
##            plt.title(boxes[i][j].name, fontsize = 7)
            plt.axis("off")
    plt.show()


def find_move_boxes(boxes):
    first_max = 0
    second_max = 0
    first_index = [-1,-1]
    second_index = [-1,-1]

    for i in range(8):
        for j in range(8):
            imgbox = boxes[i][j].image
            imgbox = cv.cvtColor(imgbox, cv.COLOR_BGR2GRAY)
            pixel_value = get_box_pixel_value(imgbox)
##            print(pixel_value, end = "\t")
            
            if pixel_value > first_max:
                second_max = first_max
                second_index = first_index
                first_max = pixel_value
                first_index = [i, j]
                
            elif pixel_value > second_max:
                second_max = pixel_value
                second_index = [i, j]
##        print()
    return [first_index, second_index]
                    

def get_box_pixel_value(img):
    total_gray_value = 0
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            total_gray_value += img[x][y]
    return total_gray_value


def move_find_threshold(img1, img2):
    img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    
    res = cv.absdiff(img1, img2)
    _, res = cv.threshold(res, 20, 255, cv.THRESH_TOZERO)
    res = cv.medianBlur(res, 9)
    return res


def  record_move(line_number, piece, frm, to, isCaptured, isCheck):
    if piece[0] == "B":
        line = "\t"
    else:
        line = str(line_number) + ". "
        
    if piece[2] == "P":
        if isCaptured:
            line += frm[0] +"x" + to
        else:
            line += to
    else:
        if isCaptured:
            line += piece[2] + "x" + to
        else:
            line += piece[2] + to

    if isCheck:
        line += "+"
    
    if piece[0] == "B":
        line += "\n"

    return line
    
