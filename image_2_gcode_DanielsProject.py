"""
5/18/23 - Sarah Propst
Purpose: translate image to gcode print path

"""
import cv2
import numpy as np

'''This function can be used to generate 2 Material prints'''

# def image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_colors, color1_ON, side1_color1_OFF, color2_ON,color2_OFF, gcode_simulate):
#     img1 = cv2.imread(image_name1, 0)
#     img2 = cv2.imread(image_name2, 0)
#
#     if gcode_simulate == True:
#         gcode_color1 = "G0 X"
#     else:
#         gcode_color1 = "G1 X"
#
#     dist = ''
#
#     prev_pixel1 = ''
#     prev_pixel2 = ''
#     gcode = ''
#     gcode_dict1 = {}
#     command_dict1 = {}
#     gcode_dict2 = {}
#     command_dict2 = {}
#
#     for i in range(len(img1)):  # for each row of pixels  (image height)
#         gcode_list1 = []
#         gcode_list2 = []
#         command_list1 = []
#         command_list2 = []
#
#         if (i + 1) % 2 == 0:  # even rows:
#             img1[i] = np.flip(img1[i])              # reverse order of pixel1
#             dist_sign = '-'                         # reverse x-direction of print
#         else:                                       # odd rows:
#             dist_sign = ''
#
#         for j in range(len(img1[i])):  # for each pixel in a row (image width)
#             pixel1 = img1[i][j]
#             pixel2 = img2[i][j]
#             if pixel1 != color1 and pixel1 != color2:
#                 pixel1 = other_colors
#             if pixel2 != color1 and pixel2 != color2:
#                 pixel2 = other_colors
#
#             if pixel1 != prev_pixel1:
#                 gcode_list1.append(dist)
#
#                 if pixel1 == color1:
#                     command_list1.append(color1_ON)
#                 elif pixel1 == color2:
#                     command_list1.append(color2_ON)
#
#                 dist = 0
#
#             if pixel2 != prev_pixel2:
#                 gcode_list2.append(dist)
#
#                 if pixel2 == color1:
#                     command_list2.append(color1_ON)
#                 elif pixel2 == color2:
#                     command_list2.append(color2_ON)
#
#                 dist = 0
#
#             dist += 1
#
#             prev_pixel1 = pixel1
#             prev_pixel2 = pixel2
#
#         gcode_dict1[i] = gcode_list1
#         gcode_dict2[i] = gcode_list2
#         command_dict1[i] = command_list1
#         command_dict2[i] = command_list2
#
#         command_dict1[i] = command_list1
#         dist = 0
#
#     return gcode_dict1, gcode_dict2, command_dict1, command_dict2
def image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_colors, side1_color1_ON, side1_color1_OFF, side1_color2_ON, side1_color2_OFF, side2_color1_ON, side2_color1_OFF, side2_color2_ON, side2_color2_OFF, gcode_simulate, simulate_side):
    img1 = cv2.imread(image_name1, 0)
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
    gcode_list = []
    command_list = []
    command_list_list = []
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
                pixel1 = other_colors

            if pixel2 != color1 and pixel2 != color2:
                pixel2 = other_colors



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
                    command_list.append(side2_color1_OFF)

                    if simulate_side != 1:
                        gcode = 'G1 X'

                pixel2_change = True

            else:
                pixel2_change = False

            if pixel1_change == True or pixel2_change == True:                         # if any of the pixels change color the distance is reset
                dist = 0

            dist += 1                                                                  # adds a 1 mm to the distance every time a pixel DOES NOT change color

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
        # command_list = []
        # gcode_list = []

    return gcode_dict, command_dict

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
image_name1 = 'test_smiley_v2.png'
image_name2 = 'Heart50x50.png'
gcode_export = 'test_Daniel.txt'


y_dist = 1  # width of filament

gcode_simulate = True   # If True: writes black (color1) pixels as 'G0' moves
simulate_side = 1     # Visualize side 1 or 2?

black = 0
white = 255

color1 = black
color2 = white
other_colors = white  # what color pixels that are not color1 or color2 be?

side1_color1_ON = 'Side 1: Black ON'
side1_color1_OFF = 'Side 1: Black OFF'

side1_color2_ON = 'Side 1: White ON'
side1_color2_OFF = 'Side 1: White OFF'

side2_color1_ON = 'Side 2: Black ON'
side2_color1_OFF = 'Side 2: Black OFF'

side2_color2_ON = 'Side 2: White ON'
side2_color2_OFF = 'Side 2: White OFF'

# gcode_list = image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_colors, color1_ON,
#                                       side1_color1_OFF, color2_ON, color2_OFF, gcode_simulate)
#
# gcode_dict1 = gcode_list[0]
# gcode_dict2 = gcode_list[1]
# command_dict1 = gcode_list[2]
# command_dict2 = gcode_list[3]
#
# print('gcode_dict1 = ', gcode_dict1)
# print('gcode_dict2 = ', gcode_dict2)
# print('command_dict1 = ', command_dict1)
# print('command_dict2 = ', command_dict2)


output = image_2_gcode_2Materials(image_name1, image_name2, y_dist, color1, color2, other_colors, side1_color1_ON, side1_color1_OFF, side1_color2_ON, side1_color2_OFF, side2_color1_ON, side2_color1_OFF, side2_color2_ON, side2_color2_OFF,gcode_simulate, simulate_side)
gcode_list = output[0]
command_list = output[1]

print('gcode_dict = ', gcode_list)
print('command_dict = ', command_list)

print(len(command_list), len(gcode_list))

print('G91')
for i in range(len(gcode_list)):
    print(gcode_list[i+1])
    for elem in command_list[i+1]:
        print(elem)
