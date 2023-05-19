"""
5/18/23 - Sarah Propst
Purpose: convert image to gcode print path

"""
import cv2
import numpy as np

'''This function does not include offsets'''
def image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_color_50_50_split, other_color_side1, other_color_side2,side1_color1_ON, side1_color1_OFF, side2_color1_ON, side2_color1_OFF, gcode_simulate, simulate_side):
    img1 = cv2.imread(image_name1, 0)
    #img2 = cv2.bitwise_not(img1)
    img2 = cv2.imread(image_name2, 0)

    if gcode_simulate == True:
        if simulate_side == 1:
            side1_gcode_color1 = "G0 X"
            side2_gcode_color1 = "G1 X"
        else:
            side1_gcode_color1 = "G1 X"
            side2_gcode_color1 = "G0 X"
    else:
        side1_gcode_color1 = "G1 X"
        side2_gcode_color1 = "G1 X"

    dist = ''
    prev_pixel1 = ''
    prev_pixel2 = ''
    gcode = ''
    gcode_dict = {}
    command_dict = {}
    command_list = []
    gcode_line_count = 0

    for i in range(len(img1)):                      # for each row of pixels  (image height) -- assumes each image is the same size
        if (i + 1) % 2 == 0:                        # even rows:
            img1[i] = np.flip(img1[i])                  # reverse order of pixels
            img2[i] = np.flip(img2[i])
            dist_sign = '-'                             # reverse x-direction of print
        else:                                       # odd rows:
            dist_sign = ''

        for j in range(len(img1[i])):  # for each pixel in a row (image width)
            pixel1 = img1[i][j]
            pixel2 = img2[i][j]

            if pixel1 != color1 and pixel1 != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel1 - color1)
                    diff_pixel_color2 = abs(pixel1 - color2)
                    pixel1 = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel1 = other_color_side1

            if pixel2 != color1 and pixel2 != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel2 - color1)
                    diff_pixel_color2 = abs(pixel2 - color2)
                    pixel2 = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel2 = other_color_side2

            '''IMAGE 1'''
            if pixel1 != prev_pixel1:
                if dist != 0:
                    gcode_line_count += 1                                                   # a gcode line is created everytime there is a change in pixel color
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist)            # stores the gcode line for the PREVIOUS grouping of pixels
                    command_list = []                                                       # clears the command list of all previous commands

                if pixel1 == color1:                                                    # if the CURRENT pixel is color1
                    command_list.append(side1_color1_ON)                                # stores commands to turn ON CURRENT pixel

                    if simulate_side != 2:  # this is just for visualization purposes
                        gcode = side1_gcode_color1

                elif pixel1 == color2:                                                  # if the CURRENT pixel is color2
                    if i > 0 and j > 0:
                        command_list.append(side1_color1_OFF)

                    if simulate_side != 2:
                        gcode = 'G1 X'

                pixel1_change = True

            else:
                pixel1_change = False

            '''IMAGE 2'''
            if pixel2 != prev_pixel2:
                if pixel1_change == False:                                                           # Only creates a new gcode line and clears the command list if image 1 and 2 don't have changes in pixel color at the same location OR if color changes does not occur at beginning row
                    gcode_line_count += 1
                    command_list = []
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist)

                if pixel2 == color1:
                    command_list.append(side2_color1_ON)

                    if simulate_side != 1:
                        gcode = side2_gcode_color1

                elif pixel2 == color2:
                    if i > 0 and j > 0:
                        command_list.append(side2_color1_OFF)

                    if simulate_side != 1:
                        gcode = 'G1 X'

                pixel2_change = True

            else:
                pixel2_change = False

            if pixel1_change == True or pixel2_change == True:    # if any of the pixels change color the distance is reset
                dist = 0

            dist += 1    # adds a 1 mm to the distance

            command_dict[gcode_line_count] = command_list                              # changes in pixel color corresponds to a line of gcode. gcode: PREVIOUS grouping of pixel colors, commands: CURRENT pixel color ON,

            prev_pixel1 = pixel1                                                       # saves the pixel color to compared to the next
            prev_pixel2 = pixel2

        command_list = []                                                              # command list is cleared at direction changes
        gcode_line_count += 1
        gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist)
        command_dict[gcode_line_count] = command_list

        gcode_line_count += 1
        gcode_dict[gcode_line_count] = 'G1 Y' + str(y_dist)
        command_dict[gcode_line_count] = command_list
        dist = 0

    return gcode_dict, command_dict

'''This function includes only one offset value (i.e., you can't have a different offset for ON and OFF) and distance between commands and edges of print is greater than offset'''
def image_2_gcode_2Materials_offset(image_name1, image_name2, y_dist, offset, color1, color2, other_color_50_50_split, other_color_side1, other_color_side2, side1_color1_ON, side1_color1_OFF, side2_color1_ON, side2_color1_OFF, gcode_simulate, simulate_side):
    img1 = cv2.imread(image_name1, 0)
    #img2 = cv2.bitwise_not(img1)
    img2 = cv2.imread(image_name2, 0)

    if gcode_simulate == True:
        if simulate_side == 1:
            side1_gcode_color1 = "G0 X"
            side2_gcode_color1 = "G1 X"
        else:
            side1_gcode_color1 = "G1 X"
            side2_gcode_color1 = "G0 X"
    else:
        side1_gcode_color1 = "G1 X"
        side2_gcode_color1 = "G1 X"

    dist = ''
    prev_pixel1 = ''
    prev_pixel2 = ''
    gcode = ''
    gcode_dict = {0: ''}
    command_dict = {}
    command_list = []
    gcode_line_count = 0

    for i in range(len(img1)):                      # for each row of pixels  (image height) -- assumes each image is the same size
        if (i + 1) % 2 == 0:                        # even rows:
            img1[i] = np.flip(img1[i])                  # reverse order of pixels
            img2[i] = np.flip(img2[i])
            dist_sign = '-'                             # reverse x-direction of print
        else:                                       # odd rows:
            dist_sign = ''

        for j in range(len(img1[i])):  # for each pixel in a row (image width)
            pixel1 = img1[i][j]
            pixel2 = img2[i][j]

            if pixel1 != color1 and pixel1 != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel1 - color1)
                    diff_pixel_color2 = abs(pixel1 - color2)
                    pixel1 = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel1 = other_color_side1

            if pixel2 != color1 and pixel2 != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel2 - color1)
                    diff_pixel_color2 = abs(pixel2 - color2)
                    pixel2 = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel2 = other_color_side2

            '''IMAGE 1'''
            if pixel1 != prev_pixel1:

                if dist != 0 and dist != '':
                    gcode_line_count += 1                                                            # a gcode line is created everytime there is a change in pixel color
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist - offset)            # stores the gcode line for the PREVIOUS grouping of pixels
                    command_list = []                                                                # clears the command list of all previous commands

                if pixel1 == color1:                                                    # if the CURRENT pixel is color1
                    command_list.append(side1_color1_ON)                                # stores commands to turn ON CURRENT pixel

                    if simulate_side != 2:  # this is just for visualization purposes
                        gcode = side1_gcode_color1

                elif pixel1 == color2:                                                  # if the CURRENT pixel is color2
                    if i > 0 and j > 0:
                        command_list.append(side1_color1_OFF)

                    if simulate_side != 2:
                        gcode = 'G1 X'

                pixel1_change = True

            else:
                pixel1_change = False

            '''IMAGE 2'''
            if pixel2 != prev_pixel2:

                if pixel1_change == False and dist != '':   # Only creates a new gcode line and clears the command list if image 1 and 2 don't have changes in pixel color at the same location OR if color changes does not occur at beginning row
                    gcode_line_count += 1
                    command_list = []
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist - offset)

                if pixel2 == color1:
                    command_list.append(side2_color1_ON)

                    if simulate_side != 1:
                        gcode = side2_gcode_color1

                elif pixel2 == color2:
                    if i > 0 and j > 0:
                        command_list.append(side2_color1_OFF)

                    if simulate_side != 1:
                        gcode = 'G1 X'

                pixel2_change = True

            else:
                pixel2_change = False

            if pixel1_change == True or pixel2_change == True:    # if any of the pixels change color the distance is reset
                dist = offset

            dist += 1    # adds a 1 mm to the distance

            command_dict[gcode_line_count] = command_list                              # changes in pixel color corresponds to a line of gcode. gcode: PREVIOUS grouping of pixel colors, commands: CURRENT pixel color ON,

            prev_pixel1 = pixel1                                                       # saves the pixel color to compared to the next
            prev_pixel2 = pixel2

        command_list = []                                                              # command list is cleared at direction changes
        gcode_line_count += 1
        gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist)
        command_dict[gcode_line_count] = command_list

        gcode_line_count += 1
        gcode_dict[gcode_line_count] = 'G1 Y' + str(y_dist)
        command_dict[gcode_line_count] = command_list
        dist = 0

    return gcode_dict, command_dict

'''This function includes both on and off offset value (i.e., you can have a different offset for ON and OFF). Currently only works correctly if the distance between commands and edges of the print is greater than the offset length'''
def image_2_gcode_2Materials_offset_Diff_OnOFF(image_name1, image_name2, y_dist, offset_ON, offset_OFF, color1, color2,other_color_50_50_split, other_color_side1, other_color_side2, side1_color1_ON, side1_color1_OFF, side2_color1_ON, side2_color1_OFF, gcode_simulate, simulate_side):
    img1 = cv2.imread(image_name1, 0)
    #img2 = cv2.bitwise_not(img1)
    img2 = cv2.imread(image_name2, 0)

    if gcode_simulate == True:
        if simulate_side == 1:
            side1_gcode_color1 = "G0 X"
            side2_gcode_color1 = "G1 X"
        else:
            side1_gcode_color1 = "G1 X"
            side2_gcode_color1 = "G0 X"
    else:
        side1_gcode_color1 = "G1 X"
        side2_gcode_color1 = "G1 X"

    dist = ''
    prev_pixel1 = ''
    prev_pixel2 = ''
    gcode = ''
    gcode_dict = {0: ''}
    command_dict = {}

    gcode_line_count = 0
    offset1 = 0
    offset2 = 0

    for i in range(len(img1)):  # for each row of pixels  (image height) -- assumes each image is the same size
        if (i + 1) % 2 == 0:  # even rows:
            img1[i] = np.flip(img1[i])  # reverse order of pixels
            img2[i] = np.flip(img2[i])
            dist_sign = '-'  # reverse x-direction of print
        else:  # odd rows:
            dist_sign = ''

        for j in range(len(img1[i])):  # for each pixel in a row (image width)
            pixel1 = img1[i][j]
            pixel2 = img2[i][j]

            if pixel1 != color1 and pixel1 != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel1 - color1)
                    diff_pixel_color2 = abs(pixel1 - color2)
                    pixel1 = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel1 = other_color_side1

            if pixel2 != color1 and pixel2 != color2:
                if other_color_50_50_split == True:
                    diff_pixel_color1 = abs(pixel2 - color1)
                    diff_pixel_color2 = abs(pixel2 - color2)
                    pixel2 = min(diff_pixel_color1, diff_pixel_color2)
                else:
                    pixel2 = other_color_side2

            '''IMAGE 1'''
            if pixel1 != prev_pixel1:
                if pixel1 == color1:  # if the CURRENT pixel is color1
                    command1 = side1_color1_ON
                    offset1 = offset_ON

                    if simulate_side == 1:  # this is just for visualization purposes
                        gcode = side1_gcode_color1

                elif pixel1 == color2:  # if the CURRENT pixel is color2
                    if i > 0 and j > 0:
                        command1 = side1_color1_OFF
                        offset1 = offset_OFF
                    else:
                        command1 = ''
                        offset1 = 0

                    if simulate_side == 1:
                        gcode = 'G1 X'

                if dist != '':
                    dist1 = dist - offset1
                pixel1_change = True

            else:
                pixel1_change = False
                command1 = ''

            '''IMAGE 2'''
            if pixel2 != prev_pixel2:
                if pixel2 == color1:
                    command2 = side2_color1_ON
                    offset2 = offset_ON

                    if simulate_side == 2:
                        gcode = side2_gcode_color1

                elif pixel2 == color2:
                    if i > 0 and j > 0:
                        command2 = side2_color1_OFF
                        offset2 = offset_OFF
                    else:
                        command2 = ''
                        offset2 = 0

                    if simulate_side == 2:
                        gcode = 'G1 X'

                if dist != '':
                    dist2 = dist - offset2

                pixel2_change = True

            else:
                pixel2_change = False
                command2 = ''


            if i == 0 and j == 0:
                command_dict[gcode_line_count] = [command1, command2]
                dist = offset_ON

            elif pixel1_change == True and pixel2_change == True:
                if offset1 == offset2:
                    gcode_line_count += 1
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist1)
                    command_dict[gcode_line_count] = [command1, command2]
                    dist = offset1

                elif offset1 > offset2:
                    gcode_line_count += 1
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist1)
                    command_dict[gcode_line_count] = [command1]
                    dist = offset1

                    gcode_line_count += 1
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist - offset2)
                    command_dict[gcode_line_count] = [command2]
                    dist = offset2

                else:
                    gcode_line_count += 1
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist2)
                    command_dict[gcode_line_count] = [command2]
                    dist = offset2

                    gcode_line_count += 1
                    gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist - offset1)
                    command_dict[gcode_line_count] = [command1]
                    dist = offset1

            if pixel1_change == True and pixel2_change == False:
                gcode_line_count += 1
                gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist1)
                command_dict[gcode_line_count] = [command1]
                dist = offset1

            elif pixel2_change == True and pixel1_change == False:
                gcode_line_count += 1
                gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist2)
                command_dict[gcode_line_count] = [command2]
                dist = offset2

            dist += 1

            prev_pixel1 = pixel1  # saves the pixel color to compared to the next
            prev_pixel2 = pixel2

        command_list = []  # command list is cleared at direction changes
        gcode_line_count += 1
        gcode_dict[gcode_line_count] = gcode + dist_sign + str(dist)
        command_dict[gcode_line_count] = command_list

        gcode_line_count += 1
        gcode_dict[gcode_line_count] = 'G1 Y' + str(y_dist)
        command_dict[gcode_line_count] = command_list
        dist = 0

    return gcode_dict, command_dict

'''
NOTES:
* photo is analyzed in greyscale
* assumes both images are the same size and shape
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
################### offset (same ON/OFF) #####################
image_name1 = 'test_smiley_v2.png'
image_name2 = 'Heart50x50.png'
gcode_export = 'test_Daniel_offset_v1.txt'

y_dist = 1  # width of filament
offset = 0

gcode_simulate = True   # If True: writes black (color1) pixels as 'G0' moves
simulate_side = 2    # Visualize side 1 or 2?

black = 0
white = 255

color1 = black        # layer color
color2 = white        # core color

# what color do you want pixels that aren't black or white?
other_color_50_50_split = False # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
other_color_side1 = black
other_color_side2 = black


side1_color1_ON = 'Side 1: Black ON'
side1_color1_OFF = 'Side 1: Black OFF'

side2_color1_ON = 'Side 2: Black ON'
side2_color1_OFF = 'Side 2: Black OFF'

core_color_ON = 'White ON'
core_color_OFF = 'White OFF'

output = image_2_gcode_2Materials_offset(image_name1, image_name2, y_dist, offset, color1, color2,
                                         other_color_50_50_split, other_color_side1, other_color_side2, side1_color1_ON,
                                         side1_color1_OFF, side2_color1_ON, side2_color1_OFF, gcode_simulate,
                                         simulate_side)
gcode_dict = output[0]
command_dict = output[1]

# print('gcode_dict = ', gcode_dict)
# print('command_dict = ', command_dict)

with open(gcode_export, 'w') as f:
    f.write('G91\r')
    f.write(core_color_ON)
    for i in range(len(gcode_dict)):
        f.write(gcode_dict[i] + '\n')
        for command in command_dict[i]:
            f.write(command + '\n')
    f.write(core_color_OFF)

################### offset (different on/off) #####################

image_name1 = 'test_smiley_v2.png'
image_name2 = 'Heart50x50.png'
gcode_export = 'test_Daniel_offset_v2.txt'

y_dist = 1  # width of filament
offset_ON = 2
offset_OFF = 2

gcode_simulate = True   # If True: writes black (color1) pixels as 'G0' moves
simulate_side = 2    # Visualize side 1 or 2?

black = 0
white = 255

color1 = black        # layer color
color2 = white        # core color

side1_color1_ON = 'Side 1: Black ON'
side1_color1_OFF = 'Side 1: Black OFF'

side2_color1_ON = 'Side 2: Black ON'
side2_color1_OFF = 'Side 2: Black OFF'

core_color_ON = 'White ON'
core_color_OFF = 'White OFF'

output = image_2_gcode_2Materials_offset_Diff_OnOFF(image_name1, image_name2, y_dist, offset_ON, offset_OFF, color1,
                                                    color2, other_color_50_50_split, other_color_side1,
                                                    other_color_side2, side1_color1_ON, side1_color1_OFF,
                                                    side2_color1_ON, side2_color1_OFF, gcode_simulate, simulate_side)
gcode_dict = output[0]
command_dict = output[1]

print('gcode_dict = ', gcode_dict)
print('command_dict = ', command_dict)

with open(gcode_export, 'w') as f:
    f.write('G91\r')
    f.write(core_color_ON)
    for i in range(len(gcode_dict)):
        f.write(gcode_dict[i] + '\n')
        for command in command_dict[i]:
            f.write(command + '\n')
    f.write(core_color_OFF)







