"""
5/16/23 - Sarah Propst
Purpose: translate image to gcode print path

"""
import cv2
import numpy as np

'''This function can be used to generate 2 Material prints'''


def image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_colors, color1_ON, color1_OFF, color2_ON,
                             color2_OFF, gcode_simulate):
    img1 = cv2.imread(image_name1, 0)
    img2 = cv2.imread(image_name2, 0)

    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    dist = ''

    prev_pixel1 = ''
    prev_pixel2 = ''
    gcode = ''
    gcode_dict1 = {}
    command_dict1 = {}
    gcode_dict2 = {}
    command_dict2 = {}

    for i in range(len(img1)):  # number of rows of pixels  (image height)
        gcode_list1 = []
        gcode_list2 = []
        command_list1 = []
        command_list2 = []

        if (i + 1) % 2 == 0:  # even rows:
            img1[i] = np.flip(img1[i])  # reverse order of pixel1
            dist_sign = '-'  # reverse x-direction of print
        else:  # odd rows:
            dist_sign = ''

        for j in range(len(img1[i])):  # number of pixels in a row (image width)
            pixel1 = img1[i][j]
            pixel2 = img2[i][j]
            if pixel1 != color1 and pixel1 != color2:
                pixel1 = other_colors
            if pixel2 != color1 and pixel2 != color2:
                pixel2 = other_colors

            if pixel1 != prev_pixel1:
                gcode_list1.append(dist)
                if pixel1 == color1:
                    command_list1.append(color1_ON)
                elif pixel1 == color2:
                    command_list1.append(color2_ON)

                dist = 0

            if pixel2 != prev_pixel2:
                gcode_list2.append(dist)

                if pixel2 == color1:
                    command_list2.append(color1_ON)
                elif pixel2 == color2:
                    command_list2.append(color2_ON)

                dist = 0

            dist += 1

            prev_pixel1 = pixel1
            prev_pixel2 = pixel2

        gcode_dict1[i] = gcode_list1
        gcode_dict2[i] = gcode_list2
        command_dict1[i] = command_list1
        command_dict2[i] = command_list2

        command_dict1[i] = command_list1
        dist = 0

    return gcode_dict1, gcode_dict2, command_dict1, command_dict2

'''
NOTES:

* photo is analyzed in greyscale
* function assumes that 1 pixel = 1 mm
* scale the image to the correct pixel numbers prior to uploading
* if orientation of the image matters (e.g., you want text to be correctly written on the top of the print), upload a mirror image of the print
* you can check the shape of your image in pixels using the following:
    img = cv2.imread(image_name, 0)
    shape = img.shape
    height_in_pixels = shape[0]
    width_in_pixels = shape[1]
    print('image height = ', height_in_pixels, ' pixels')
    print('image width = ', width_in_pixels, ' pixels')


'''
############################################### 2 Colors function ################################
image_name1 = 'test_smiley.png'
image_name2 = 'Heart50x50.png'
gcode_export = 'test_Daniel.txt'


y_dist = 1  # width of filament

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
black = 0
white = 255

color1 = black
color2 = white
other_colors = white  # what color pixels that are not color1 or color2 be?

color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'

gcode_list = image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_colors, color1_ON,
                                      color1_OFF, color2_ON, color2_OFF, gcode_simulate)

gcode_dict1 = gcode_list[0]
gcode_dict2 = gcode_list[1]
command_dict1 = gcode_list[2]
command_dict2 = gcode_list[3]

print('gcode_dict1 = ', gcode_dict1)
print('gcode_dict2 = ', gcode_dict2)
print('command_dict1 = ', command_dict1)
print('command_dict2 = ', command_dict2)

for i in range(len(gcode_dict1)):

