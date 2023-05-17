"""
5/16/23 - Sarah Propst
Purpose: translate image to gcode print path

"""
import cv2
import numpy as np

'''This function can be used to generate 2 Material prints'''
def image_2_gcode_2Materials(image_name, y_dist, color1, color2, other_colors, color1_ON, color1_OFF, color2_ON, color2_OFF, gcode_simulate):
    img = cv2.imread(image_name, 0)

    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    dist = ''
    prev_pixel = ''
    gcode = ''
    gcode_list = []
    for i in range(len(img)):               # number of rows of pixels  (image height)
        if (i + 1) % 2 == 0:                # even rows:
            img[i] = np.flip(img[i])        # reverse order of pixel
            dist_sign = '-'                 # reverse x-direction of print
        else:                               # odd rows:
            dist_sign = ''

        for j in range(len(img[i])):        # number of pixels in a row (image width)
            pixel = img[i][j]

            if pixel != color1 and pixel != color2:
                pixel = other_colors

            if pixel == color1:
                if prev_pixel != color1:
                    gcode_list.append(gcode + dist_sign + str(dist))
                    gcode_list.append(color1_ON)
                    gcode_list.append(color2_OFF)
                    dist = 0

                gcode = gcode_color1


            if pixel == color2 or pixel == other_colors:
                pixel = color2
                if prev_pixel != color2:
                    gcode_list.append(gcode + dist_sign + str(dist))
                    gcode_list.append(color2_ON)
                    gcode_list.append(color1_OFF)
                    dist = 0

                gcode = "G1 X"

            dist += 1
            prev_pixel = pixel


        gcode_list.append(gcode + dist_sign + str(dist))
        gcode_list.append('G1 Y'+str(y_dist))

        dist = 0
        if i == len(img) - 1:
            if pixel == color1:
                gcode_list.append(color1_OFF)
            if pixel == color2:
                gcode_list.append(color2_OFF)
    return gcode_list

'''This function can be used to generate 2+ Material prints'''
def image_2_gcode_2plusMaterials(image_name, color_list, other_colors, color_ON_list, color_OFF_list):
    img = cv2.imread(image_name, 0)

    dist = ''
    prev_pixel = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []
    for i in range(len(img)):  # number of rows of pixels  (image height)
        if (i + 1) % 2 == 0:  # even rows:
            img[i] = np.flip(img[i])  # reverse order of pixel
            dist_sign = '-'  # reverse x-direction of print
        else:  # odd rows:
            dist_sign = ''

        for j in range(len(img[i])):  # number of pixels in a row (image width)
            pixel = img[i][j]

            if pixel not in color_list:
                pixel = other_colors

            for k in range(len(color_list)):
                color = color_list[k]

                if pixel == color:
                    color_ON = color_ON_list[k]
                    color_OFF = color_OFF_list[k]

                    if prev_pixel != color:
                        gcode_list.append(gcode + dist_sign + str(dist))
                        gcode_list.append(color_ON)

                        if i != 0:
                            gcode_list.append(prev_color_OFF)
                        dist = 0

                    gcode = 'G1 X'

                    try:
                        dist += 1
                    except:
                        dist = ''

            prev_pixel = pixel
            prev_color_OFF = color_OFF

        gcode_list.append(gcode + dist_sign + str(dist))
        gcode_list.append('G1 Y1')

        dist = 0
        if i == len(img) - 1:
            gcode_list.append(color_OFF)
    return gcode_list

'''
NOTES:

* function assumes that 1 pixel = 1 mm
* scale the image to the correct pixel numbers prior to uploading
* you can check the shape of your image in pixels using the following:
    img = cv2.imread(image_name, 0)
    shape = img.shape
    height_in_pixels = shape[0]
    width_in_pixels = shape[1]
    print('image height = ', height_in_pixels, ' pixels')
    print('imiage width = ', width_in_pixels, ' pixels')
   
'''
############################################### 2 Colors function ################################
image_name = 'test_smiley_v2.png'
gcode_export = 'test_smiley_v2_2Material.txt'

img = cv2.imread(image_name, 0)
shape = img.shape
height_in_pixels = shape[0]
width_in_pixels = shape[1]
print('image height = ', height_in_pixels, ' pixels')
print('image width = ', width_in_pixels, ' pixels')


y_dist = 1   # width of filament

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

gcode_list = image_2_gcode_2Materials(image_name, y_dist, color1, color2, other_colors, color1_ON, color1_OFF,
                                      color2_ON, color2_OFF, gcode_simulate)
with open(gcode_export, 'w') as f:
    f.write('G91\r')
    for elem in gcode_list:
        f.write(elem +'\n')


############################################### 2+ Colors function ################################
image_name = 'test_smiley.png'
gcode_export = 'test_smiley_3Material.txt'

black = 0
white = 255
gray = 191

color1 = black
color2 = white
color3 = gray

color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'
color3_ON = 'Gray ON'
color3_OFF = 'Gray OFF'

color_list = [black, white, gray]
other_colors = gray  # what color should pixels that are not in color list be?
color_ON_list = [color1_ON, color2_ON, color3_ON]
color_OFF_list = [color1_OFF, color2_OFF, color3_OFF]

gcode_list = image_2_gcode_2plusMaterials(image_name,color_list, other_colors, color_ON_list, color_OFF_list)
with open(gcode_export, 'w') as f:
    f.write('G91\r')
    for elem in gcode_list:
        f.write(elem +'\n')
