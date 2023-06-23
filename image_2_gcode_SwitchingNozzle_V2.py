"""
5/16/23 - Sarah Propst
Purpose: convert image to gcode print path


Notes:
    * set scale to how many mm = 1 pixel
    * for decimal offsets (i.e., 1.25, 1.5, etc) scale the width of the picture by (1/scale) (e.g., 75 x 75 pix, with 0.25 mm = 1 pixel --> 75/0.25 x 75 pix)
    * offset/scale must equal an integar
"""
import cv2
import numpy as np


def rgb_to_hex(b, g, r):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

'''This function can be used to generate 2+ Material prints'''
def image_2_gcode_2plusMaterials(image_name, y_dist, offset, color_list, other_color_50_50_split, other_color,color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, color_code, scale_x, scale_y):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    # for elem in cv2.imread(image_name)[35]:
    #     if list(elem) == [229, 172, 104]:
    #         print(True)

    if color_code == 'HEX':
        img = cv2.imread(image_name)

    elif color_code == 'RGB':
        img = cv2.imread(image_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif color_code == 'Grayscale':
        img = cv2.imread(image_name, 0)

    img = cv2.flip(img, 1) # this makes sure the image is not backwards
    img = cv2.resize(img, None, fx = 1/scale_x, fy = 1/scale_y,interpolation= cv2.INTER_LINEAR)

    dist = 0
    prev_pixel = ''
    prev_color_OFF = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []

    if offset == 0:
        offset = 0


    elif scale_x != scale_y:
        offset = int(offset/scale_x) - y_dist
    else:
        offset = int((offset-y_dist)/scale_x)

    for i in range(len(img)):  # number of rows of pixels  (image height)
        current_image = img[i]
        if color_code == 'HEX':
            raw_current_image = img[i]
            current_image = []
            for elem in raw_current_image:
                pixel = elem
                pixel = rgb_to_hex(pixel[0], pixel[1], pixel[2])
                current_image.append(pixel)

        if i != len(img) - 1: # will be used in the offset
            next_image = img[i+1]
            if color_code == 'HEX':
                raw_next_image = img[i+1]
                next_image = []
                for elem in raw_next_image:
                    pixel = elem
                    pixel = rgb_to_hex(pixel[0], pixel[1], pixel[2])
                    next_image.append(pixel)

        if (i + 1) % 2 == 0:  # even rows:
            current_image = np.flip(current_image)  # reverse order of pixel
            dist_sign = '-'  # reverse x-direction of print

        else:  # odd rows:
            next_image = np.flip(next_image)
            dist_sign = ''

        if i > 0:
            current_image = current_image[offset:]

        next_image = next_image[0:offset]

        pixels_to_print = np.concatenate((current_image, next_image), axis=0)#np.append(current_image, next_image)

        if i == len(img) - 1:
            pixels_to_print = current_image

        for j in range(len(pixels_to_print)):  # number of pixels in a row (image width)
            pixel = list(pixels_to_print[j])

            if pixel not in color_list:
                if other_color_50_50_split == True and color_code == 'Grayscale':  # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
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

                if dist != 0:
                    gcode_list.append(gcode + dist_sign + str(dist))

                gcode_list.append(color_ON)

                if i > 0 or j > 0:
                    gcode_list.append(prev_color_OFF)

                dist = 0

                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1


            dist += scale_x

            prev_pixel = pixel
            prev_color_OFF = color_OFF

        gcode_list.append(gcode + dist_sign + str(dist))
        if i == len(img)-1:
            gcode_list.append(prev_color_OFF)
            gcode_list.append(gcode + dist_sign + str(offset))


        gcode_list.append('G1 Y' + str(y_dist))
        dist = 0


    return gcode_list

############################################### 2+ Colors function ################################
image_name = 'checkerboard_30x30pix.png'
gcode_export = '----TEST----.txt'

img = cv2.imread(image_name)
pix_hex_list = []

y_dist = 1  # width of filament/nozzle
offset = 10

scale_x =1 # 1 pixel = [scale] mm
scale_y = 1

color_code = 'RGB' # 'HEX', 'Grayscale'

if color_code == 'HEX':
    ## HEX:
    black = '#000000'
    white = '#ffffff'
    blue = '#68ace5'

elif color_code == 'RGB':
    black = [0, 0, 0]
    white = [255, 255, 255]
    blue = [104, 172, 229]

else:
    ## Grayscale:
    black = 0
    white = 255
    blue = 150

color1 = black
color2 = white
color3 = blue

# what color do you want pixels that aren't black or white?
other_color_50_50_split = False  # ONly works in grayscale mode; True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
other_color = black

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = color1

color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'
color3_ON = 'Blue ON'
color3_OFF = 'Blue OFF'


color_list = [color1, color2, color3]
color_ON_list = [color1_ON, color2_ON, color3_ON]
color_OFF_list = [color1_OFF, color2_OFF, color3_OFF]

gcode_list_2plus_colors = image_2_gcode_2plusMaterials(image_name, y_dist, offset, color_list, other_color_50_50_split,other_color, color_ON_list, color_OFF_list, gcode_simulate,gcode_simulate_color, color_code, scale_x, scale_y)


with open(gcode_export, 'w') as f:
    f.write('G91\r')
    for elem in gcode_list_2plus_colors:
        f.write(elem + '\n')

