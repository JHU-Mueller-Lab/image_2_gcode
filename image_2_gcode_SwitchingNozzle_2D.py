"""
5/16/23 - Sarah Propst
Purpose: convert image to gcode print path

"""
import cv2
import numpy as np
def rgb_to_hex(b, g, r):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


'''This function can be used to generate 2 Material prints'''
def image_2_gcode_2Materials(image_name, y_dist, offset, color1, color2,other_color_50_50_split, other_color, color1_ON, color1_OFF, color2_ON, color2_OFF, gcode_simulate):
    img = cv2.imread(image_name, 0)

    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    dist = ''
    prev_pixel = ''
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

            if pixel != color1 and pixel != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel - color1)
                    diff_pixel_color2 = abs(pixel - color2)
                    pixel = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel = other_color

            if pixel == color1:
                if prev_pixel != color1:
                    if i > 0 and j > 0:
                        gcode_list.append(gcode + dist_sign + str(dist-offset))

                    gcode_list.append(color1_ON)

                    if i > 0 and j> 0:
                        gcode_list.append(color2_OFF)
                    dist = offset

                gcode = gcode_color1

            if pixel == color2:
                pixel = color2
                if prev_pixel != color2:
                    if i > 0 and j > 0:
                        gcode_list.append(gcode + dist_sign + str(dist-offset))
                    gcode_list.append(color2_ON)

                    if i > 0 and j > 0:
                        gcode_list.append(color1_OFF)
                    dist = offset

                gcode = "G1 X"

            try:
                dist += 1
            except:
                dist = 1

            prev_pixel = pixel

        gcode_list.append(gcode + dist_sign + str(dist))
        gcode_list.append('G1 Y' + str(y_dist))

        dist = 0
        if i == len(img) - 1:
            if pixel == color1:
                gcode_list.append(color1_OFF)
            if pixel == color2:
                gcode_list.append(color2_OFF)
    return gcode_list

'''This function can be used to generate 2+ Material prints'''
def image_2_gcode_2plusMaterials(image_name, y_dist, offset, color_list, other_color_50_50_split, other_color, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, convert_to_hex):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    img = cv2.imread(image_name, 0)
    if convert_to_hex == True:
        img = cv2.imread(image_name)

    img = cv2.flip(img, 1)
    # cv2.imshow('flipped', img)
    # cv2.waitKey(0)
    #

    dist = ''
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
                #pix_hex_list.append(pix_hex)

            if pixel not in color_list:
                if other_color_50_50_split == True and convert_to_hex == False: # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
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

                if i > 0 and j> 0:
                    gcode_list.append(prev_color_OFF)

                dist = offset

                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1



            try:
                dist += 1
            except:
                dist = 1

            prev_pixel = pixel
            prev_color_OFF = color_OFF

        gcode_list.append(gcode + dist_sign + str(dist))
        gcode_list.append('G1 Y' + str(y_dist))

        dist = 0
        if i == len(img) - 1:
            gcode_list.append(color_OFF)
    return gcode_list

'''This function can be used to generate 2+ Material prints with different on/off offsets'''
def image_2_gcode_2plusMaterials_diffOnOff_offsets(image_name, y_dist, offset_ON, offset_OFF, color_list, other_color_50_50_split, other_color, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    img = cv2.imread(image_name, 0)

    dist = ''
    prev_pixel = ''
    prev_color_OFF = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []

    offset_largest = max(offset_ON, offset_OFF)
    offset_smallest = min(offset_ON, offset_OFF)

    for i in range(len(img)):  # number of rows of pixels  (image height)
        if (i + 1) % 2 == 0:  # even rows:
            img[i] = np.flip(img[i])  # reverse order of pixel
            dist_sign = '-'  # reverse x-direction of print
        else:  # odd rows:
            dist_sign = ''

        for j in range(len(img[i])):  # number of pixels in a row (image width)
            pixel = img[i][j]

            if pixel not in color_list:
                if other_color_50_50_split == True:  # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
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

                if offset_ON > offset_OFF:
                    largest_offset_toggle = color_ON
                    smallest_offset_toggle = prev_color_OFF
                else:
                    smallest_offset_toggle = color_ON
                    largest_offset_toggle = prev_color_OFF

                if i > 0 and j > 0:
                    gcode_list.append(gcode + dist_sign + str(dist - offset_largest))
                    dist = offset_largest
                    gcode_list.append(largest_offset_toggle)
                    gcode_list.append(gcode + dist_sign + str(dist - offset_smallest))
                    dist = offset_smallest
                    gcode_list.append(smallest_offset_toggle)

                else:
                    gcode_list.append(color_ON)
                    dist = offset_ON


                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1

            try:
                dist += 1
            except:
                dist = 1

            prev_pixel = pixel
            prev_color_OFF = color_OFF
            prev_offset_smallest = offset_smallest

        gcode_list.append(gcode + dist_sign + str(dist))
        gcode_list.append('G1 Y' + str(y_dist))

        dist = 0
        if i == len(img) - 1:
            gcode_list.append(color_OFF)
    return gcode_list

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
    
* CURRENT VERSION: offset variable applies to both ON and OFF
* CURRENT VERSION: distance between edge of print and image must be greater than the offset
* CURRENT VERSION for V2 offsets (DIFFERENT ON/OFF offsets): for some reason offset values can only be .5 different....
    
'''
############################################### 2 Colors function ################################
image_name = 'blue_jay_75x75pics.png'
gcode_export = 'blue_jay_75x75pics_2Material.txt'

y_dist = 1  # width of filament
offset = 0

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
black = 0
white = 255

color1 = black
color2 = white

# what color do you want pixels that aren't black or white?
other_color_50_50_split = True # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
other_color = white


color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'

gcode_list_2colors = image_2_gcode_2Materials(image_name, y_dist, offset, color1, color2,other_color_50_50_split, other_color, color1_ON, color1_OFF, color2_ON, color2_OFF, gcode_simulate)

with open(gcode_export, 'w') as f:
    f.write('G91\r')
    for elem in gcode_list_2colors:
        f.write(elem + '\n')

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
    blue =  '#68ace5'

else:
    ## Grayscale:
    black = 0
    white = 255
    gray = 150

color1 = black
color2 = white
color3 = blue

# what color do you want pixels that aren't black or white?
other_color_50_50_split = True # ONly works in grayscale mode; True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
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

gcode_list_2plus_colors = image_2_gcode_2plusMaterials(image_name, y_dist, offset, color_list, other_color_50_50_split,
                                                       other_color, color_ON_list, color_OFF_list, gcode_simulate,
                                                       gcode_simulate_color, convert_to_hex)
with open(gcode_export, 'w') as f:
    f.write('G91\r')
    for elem in gcode_list_2plus_colors:
        f.write(elem + '\n')


############################################### Different ON/OFF offsets: 2+ Colors function ################################
image_name = 'test_smiley_v2.png'
gcode_export = 'test_smiley_v2_3Material_diff_OFFSETS.txt'

y_dist = 1  # width of filament
offset_ON = 0
offset_OFF = 0

black = 0
white = 255
gray = 191

color1 = black
color2 = white
color3 = gray

# what color do you want pixels that aren't black or white?
other_color_50_50_split = False # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
other_color = gray

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = black


color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'
color3_ON = 'Gray ON'
color3_OFF = 'Gray OFF'

color_list = [black, white, gray]
color_ON_list = [color1_ON, color2_ON, color3_ON]
color_OFF_list = [color1_OFF, color2_OFF, color3_OFF]

gcode_list_2plus_diff_offsets = image_2_gcode_2plusMaterials_diffOnOff_offsets(image_name, y_dist, offset_ON,
                                                                               offset_OFF, color_list,
                                                                               other_color_50_50_split, other_color,
                                                                               color_ON_list, color_OFF_list,
                                                                               gcode_simulate, gcode_simulate_color)
with open(gcode_export, 'w') as f:
    f.write('G91\r')
    for elem in gcode_list_2plus_diff_offsets:
        f.write(elem + '\n')

