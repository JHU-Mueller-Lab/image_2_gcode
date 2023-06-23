"""
5/16/23 - Sarah Propst
Purpose: convert image to gcode print path

"""
import cv2
import numpy as np


def rgb_to_hex(b, g, r):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

'''This function can be used to generate 2+ Material prints'''
def image_2_gcode_2plusMaterials(image_name, y_dist, offset, color_list, other_color_50_50_split, other_color,color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, convert_to_hex):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    img = cv2.imread(image_name, 0)
    if convert_to_hex == True:
        img = cv2.imread(image_name)

    img = cv2.flip(img, 1) # this makes sure the image is not backwards

    dist = 0
    prev_pixel = ''
    prev_color_OFF = ''
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

            if convert_to_hex == True:
                pixel = rgb_to_hex(pixel[0], pixel[1], pixel[2])
                # pix_hex_list.append(pix_hex)

            if pixel not in color_list:
                if other_color_50_50_split == True and convert_to_hex == False:  # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
                    diff_pixel = []
                    for color in range(len(color_list)):
                        diff_pixel.append(abs(pixel - color))
                    pixel = np.min(diff_pixel)

                else:
                    pixel = other_color

            if prev_pixel != pixel:
                for k in range(len(color_list)):
                    color = color_list[k]

                    if pixel == color:
                        color_ON = color_ON_list[k]
                        color_OFF = color_OFF_list[k]

                if i > 0 and j > 0:
                    gcode_list.append(gcode + dist_sign + str(dist - offset))

                gcode_list.append(color_ON)

                if i > 0 and j > 0:
                    gcode_list.append(prev_color_OFF)

                dist = offset

                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1


            dist += 1

            prev_pixel = pixel
            prev_color_OFF = color_OFF

        gcode_list.append(gcode + dist_sign + str(dist))
        gcode_list.append('G1 Y' + str(y_dist))

        dist = 0
        if i == len(img) - 1:
            gcode_list.append(color_OFF)

    return gcode_list


############################################### 2+ Colors function ################################
image_name = 'blue_jay_75x75pixs_3colors.png'
gcode_export = 'blue_jay_75x75pixs_3colors_3Material.txt'

img = cv2.imread(image_name)
pix_hex_list = []

y_dist = 1  # width of filament
offset = 0

convert_to_hex = True
if convert_to_hex == True:
    ## HEX:
    black = '#000000'
    white = '#ffffff'
    blue = '#68ace5'

else:
    ## Grayscale:
    black = 0
    white = 255
    gray = 150

color1 = black
color2 = white
color3 = blue

# what color do you want pixels that aren't black or white?
other_color_50_50_split = True  # ONly works in grayscale mode; True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
other_color = blue

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = color1

color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'
color3_ON = 'Gray ON'
color3_OFF = 'Gray OFF'

color_list = [color1, color2, color3]
color_ON_list = [color1_ON, color2_ON, color3_ON]
color_OFF_list = [color1_OFF, color2_OFF, color3_OFF]

# gcode_list_2plus_colors = image_2_gcode_2plusMaterials(image_name, y_dist, offset, color_list, other_color_50_50_split,other_color, color_ON_list, color_OFF_list, gcode_simulate,gcode_simulate_color, convert_to_hex)
#
# with open(gcode_export, 'w') as f:
#     f.write('G91\r')
#     for elem in gcode_list_2plus_colors:
#         f.write(elem + '\n')

