"""
5/16/23 - Sarah Propst
Purpose: translate image to gcode print path

"""
import numpy as np
import cv2
import pandas as pd
import numpy as np

image_name = 'pyramid_v1.png'
img = cv2.imread(image_name, 0)
cv2.imshow('Image', img)

# counting the number of pixels
number_of_white_pix = np.sum(img == 255)
number_of_black_pix = np.sum(img == 0)


flipped = np.flip(img[-1])
print(flipped)

white = 255
black = 0

black_ON = False
white_ON = False
dist = 0
# for i in range(len(img)):
#     if (i+1)%2 == 0:
#         img[i] = np.flip(img[i])
#
#     for j in range(len(img[i])):
#         pixel = img[i][j]
#
#         if pixel == black:
#             gcode = 'G0 X'
#             if white_ON == True:
#                 if (i+1)%2 == 0:
#                     dist = -dist
#                 print(gcode+str(dist))
#                 print("black ON")
#                 print("white OFF")
#                 dist = 0
#
#             black_ON = True
#             white_ON = False
#             dist += 1
#             # if (i + 1) % 2 == 0:
#             #     dist -= 1
#             # else:
#             #     dist += 1
#
#         #if pixel == white:
#         else:
#             gcode = 'G1 X'
#             if black_ON == True:
#                 if (i+1)%2 == 0:
#                     dist = -dist
#                 print(gcode + str(dist))
#                 print("white ON")
#                 print("black OFF")
#                 dist = 0
#             dist += 1
#             white_ON = True
#             black_ON = False
#             # if (i + 1) % 2 == 0:
#             #     dist -= 1
#             # else:
#             #     dist += 1
#
#     if (i+1)%2 == 0:
#         dist = -dist
#     print(gcode + str(dist))
#     print('G1 Y1')
#     dist = 0



for i in range(len(img)):
    print_sign = ''
    if (i+1)%2 == 0:
        img[i] = np.flip(img[i])
        print_sign = '-'

    for j in range(len(img[i])):
        pixel = img[i][j]
        if pixel == black:
            gcode = 'G0 X'
            if white_ON == True:
                print(gcode + str(print_sign) + str(dist))
                print("black ON")
                print("white OFF")
                dist = 0

            dist +=1
            black_ON = True
            white_ON = False
        else:
            gcode = 'G1 X'
            if black_ON == True:
                print(gcode + str(print_sign) + str(dist))
                print("white ON")
                print("black OFF")
                dist = 0

            dist += 1
            black_ON = False
            white_ON = True
        if j == len(img[i])-1:
            print(gcode + str(print_sign) + str(dist))
            print('G1 Y1')
            print(j)

    dist = 0

print(len(img[-1]))
