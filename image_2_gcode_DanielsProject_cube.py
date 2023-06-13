import cv2
import numpy as np

'''NOTES
* all images must be the same size
* 1 pixel = 1 mm
* smallest feature must be > offset
* distance to edge must > offset 
'''


def image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, wall_thickness, offset_ON, offset_OFF):
    black = 0
    white = 255
    img_list = []
    for image in image_list:
        img = cv2.imread(image, 0)
        img = cv2.flip(img, 0)  # flip over y-axis
        img_list.append(img)  # converts images to pixels

    img_shape = img_list[0].shape  # finds width and height of image (will use the first image in the last)
    height = img_shape[0]
    width = img_shape[1]

    num_layers = int(height)

    ### This section creates the spiral print path
    if wall_thickness == 'solid':
        current_length = fil_width
    else:
        current_length = width - (2 * wall_thickness - 1)


    p_list_A = []  # relative coordinate
    dir_list_A = []  # direction of nozzle
    face_list_A = []  # face on the cube

    # for wall in range(wall_thickness):
    while current_length < width:

        if current_length == fil_width:
            p_start = [current_length, 0]
            p_list_A.append(p_start)
            dir_list_A.append('East')  # direction of nozzle
            face_list_A.append('South')  # face on the cube

        # N -> W -> S -> E (A layers go outward)
        p1 = [0, current_length]  # NORTH

        current_length += fil_width

        p2 = [-current_length, 0]  # WEST
        p3 = [0, -current_length]  # SOUTH

        if current_length < width:
            current_length += fil_width

        p4 = [current_length, 0]  # EAST

        p_list_A.append(p1)
        dir_list_A.append('North')  # direction of nozzle
        face_list_A.append('East')  # face on the cube

        p_list_A.append(p2)
        dir_list_A.append('West')
        face_list_A.append('North')

        p_list_A.append(p3)
        dir_list_A.append('South')
        face_list_A.append('West')

        p_list_A.append(p4)
        dir_list_A.append('East')
        face_list_A.append('South')

    # B layers go inward
    p_list_A_reversed = list(reversed(p_list_A))
    dir_list_A_reversed = list(reversed(dir_list_A))

    p_list_B = []
    dir_list_B = []
    for layer in range(len(p_list_A_reversed)):
        coord_even = []
        for coordinates in p_list_A_reversed[layer]:
            coord_even.append(-coordinates)

        p_list_B.append(coord_even)

    for dir in dir_list_A_reversed:
        if dir == 'North':
            dir_list_B.append('South')
        elif dir == 'South':
            dir_list_B.append('North')
        elif dir == 'West':
            dir_list_B.append('East')
        else:
            dir_list_B.append('West')

    face_list_B = list(reversed(face_list_A))

    outer_face_short = face_list_A[-4]  # edge of this face will have 1 mm used for +z
    print(p_list_A)
    print(p_list_B)

    ## This section makes sure the final layer does not have dollop in the center
    if height % 2 != 0:  # if the height is an odd number
        p_list_odd = p_list_A
        dir_list_odd = dir_list_A
        face_list_odd = face_list_A

        p_list_even = p_list_B
        dir_list_even = dir_list_B
        face_list_even = face_list_B

        outer_edge_list_odd = p_list_odd[-4:]
        outer_edge_list_even = p_list_even[0:4]

        reverse_pixels = 'even'  # reverses pixels when layer is even

    else:
        p_list_odd = p_list_B
        dir_list_odd = dir_list_B
        face_list_odd = face_list_B

        p_list_even = p_list_A
        dir_list_even = dir_list_A
        face_list_even = face_list_A

        outer_edge_list_odd = p_list_odd[0:4]
        outer_edge_list_even = p_list_even[-4:]

        reverse_pixels = 'odd'  # reverses pixels when layer is odd

    print(outer_edge_list_odd)
    print(outer_edge_list_even)
    # print(reverse_pixels)

    #### This section creates the final print path that will be used
    dirNorth_faceEast_ON = toggle_ON_list[0]
    dirNorth_faceWest_ON = toggle_ON_list[1]
    dirSouth_faceEast_ON = toggle_ON_list[2]
    dirSouth_faceWest_ON = toggle_ON_list[3]
    dirWest_faceNorth_ON = toggle_ON_list[4]
    dirWest_faceSouth_ON = toggle_ON_list[5]
    dirEast_faceNorth_ON = toggle_ON_list[6]
    dirEast_faceSouth_ON = toggle_ON_list[7]

    dirNorth_faceEast_OFF = toggle_OFF_list[0]
    dirNorth_faceWest_OFF = toggle_OFF_list[1]
    dirSouth_faceEast_OFF = toggle_OFF_list[2]
    dirSouth_faceWest_OFF = toggle_OFF_list[3]
    dirWest_faceNorth_OFF = toggle_OFF_list[4]
    dirWest_faceSouth_OFF = toggle_OFF_list[5]
    dirEast_faceNorth_OFF = toggle_OFF_list[6]
    dirEast_faceSouth_OFF = toggle_OFF_list[7]

    z = z_height
    prev_pixel = ''
    prev_valve_OFF = ''

    if visualize_ON == True:
        z_var = "Z"

    print('G91')
    dist_list = []
    var_list = []
    command_list = []
    G_list = []
    for layer in range(num_layers):
        print(';---LAYER-----', layer + 1)
        if (layer + 1) % 2 != 0:
            layer_flag = 'odd'
            p_list = p_list_odd
            face_list = face_list_odd
            dir_list = dir_list_odd
            outer_edge_list = outer_edge_list_odd

        else:
            layer_flag = 'even'
            p_list = p_list_even
            face_list = face_list_even
            dir_list = dir_list_even
            outer_edge_list = outer_edge_list_even

        print('---outer edge---', outer_edge_list)


        for coordinates in range(len(p_list)):
            if p_list[coordinates] not in outer_edge_list:
                print('G1 X' + str(p_list[coordinates][0]) + ' Y' + str(p_list[coordinates][1]))

                ##### create distance and variable list
                for i in range(len(p_list[coordinates])):
                    dist = p_list[coordinates][i]

                    if dist != 0:
                        if i == 0:
                            var = 'X'
                        else:
                            var = 'Y'

                        dist_list.append(dist)
                        var_list.append(var)
                        command_list.append('')
                        G_list.append('G1')


            elif p_list[coordinates] in outer_edge_list:

                current_face = face_list[coordinates]
                current_dir = dir_list[coordinates]
                print(';---current face----', current_face)
                print(';---current dir----', current_dir)

                if current_dir == 'North':
                    if current_face == 'East':
                        valve_on = dirNorth_faceEast_ON
                        valve_OFF = dirNorth_faceEast_OFF
                    elif current_face == 'West':
                        valve_on = dirNorth_faceWest_ON
                        valve_OFF = dirNorth_faceWest_OFF

                    variable = 'Y'
                    sign = 1

                if current_dir == 'South':
                    if current_face == 'East':
                        valve_on = dirSouth_faceEast_ON
                        valve_OFF = dirSouth_faceEast_OFF
                    elif current_face == 'West':
                        valve_on = dirSouth_faceWest_ON
                        valve_OFF = dirSouth_faceWest_OFF

                    variable = 'Y'
                    sign = -1

                if current_dir == 'East':
                    if current_face == 'North':
                        valve_on = dirEast_faceNorth_ON
                        valve_OFF = dirEast_faceNorth_OFF
                    elif current_face == 'South':
                        valve_on = dirEast_faceSouth_ON
                        valve_OFF = dirEast_faceSouth_OFF
                    variable = 'X'
                    sign = 1

                if current_dir == 'West':
                    if current_face == 'North':
                        valve_on = dirWest_faceNorth_ON
                        valve_OFF = dirWest_faceNorth_OFF
                    elif current_face == 'South':
                        valve_on = dirWest_faceSouth_ON
                        valve_OFF = dirWest_faceSouth_OFF

                    variable = 'X'
                    sign = -1

                if current_face == 'East':  # Image 1, nozzle moving North or South
                    current_img = img_list[0][layer]

                if current_face == 'North':  # Image 2, nozzle moving East or West
                    current_img = img_list[1][layer]
                    # current_img = current_img[1:]

                if current_face == 'West':  # Image 3, nozzle moving North or South
                    current_img = img_list[2][layer]

                if current_face == 'South':  # Image 4, nozzle moving East or West
                    current_img = img_list[3][layer]

                if current_face == outer_face_short:  # edge of img (first pixel) is replaced by +Z movement
                    current_img = current_img[1:]

                if layer_flag == reverse_pixels:
                    current_img = np.flip(current_img)

                current_distance = 0
                current_distance_no_offset = 0
                offset = 0

                for pixel in current_img:
                    if pixel != white:
                        pixel = black

                    if prev_pixel != pixel:
                        if pixel == black:
                            offset = offset_ON
                            print('G1 ' + str(variable) + str(sign*(current_distance - offset)))
                            print(valve_on)

                            dist_list.append(sign*current_distance_no_offset)
                            var_list.append(variable)
                            command_list.append(valve_on)
                            G_list.append('G1')



                        elif pixel != black and prev_pixel != '':
                            offset = offset_OFF
                            if visualize_ON == True:
                                print('G0 ' + str(variable) + str(sign*(current_distance - offset)))
                                G_list.append('G0')

                            else:
                                print('G1 ' + str(variable) + str(sign*(current_distance - offset)))
                                G_list.append('G1')
                            print(prev_valve_OFF)

                            dist_list.append(sign*current_distance_no_offset)
                            var_list.append(variable)
                            command_list.append(valve_OFF)


                        current_distance = offset
                        current_distance_no_offset = 0

                    current_distance += 1
                    current_distance_no_offset +=1
                    prev_pixel = pixel
                    prev_valve_OFF = valve_OFF

                print('G1 ' + str(variable) + str(sign*(current_distance)))

                dist_list.append(sign*current_distance_no_offset)
                var_list.append(variable)
                command_list.append('')
                G_list.append('G1')

        print('G1 ' + str(z_var) + str(z))
        dist_list.append(z)
        var_list.append(z_var)
        command_list.append('')
        G_list.append('G1')

    return G_list, var_list, dist_list, command_list



def spiral_matrix(image):
    img = cv2.imread(image, 0)
    img_shape = img.shape  # finds width and height of image (will use the first image in the last)
    height = img_shape[0]
    width = img_shape[1]

    top = 0
    bottom = height - 1
    left = 0
    right = width - 1

    ## source code: https://www.educative.io/answers/spiral-matrix-algorithm
    while (top <= bottom and left <=right):
        dir = 2 # starting direction  (right --> left starting at bottom)
        while (top <= bottom and left <= right):
            if dir == 0:
                for i in range(left, right + 1):  # moving left->right
                    print(img[top][i], end=" ")

                # Since we have traversed the whole first
                # row, move down to the next row.
                top += 1
                dir = 1

            elif dir == 1:
                for i in range(top, bottom + 1):  # moving top->bottom
                    print(img[i][right], end=" ")

                # Since we have traversed the whole last
                # column, move down to the previous column.
                right -= 1
                dir = 2

            elif dir == 2:
                for i in range(right, left - 1, -1):  # moving right->left
                    print(img[bottom][i], end=" ")

                # Since we have traversed the whole last
                # row, move down to the previous row.
                bottom -= 1
                dir = 3

            elif dir == 3:
                for i in range(bottom, top - 1, -1):  # moving bottom->top
                    print(img[i][left], end=" ")
                # Since we have traversed the whole first
                # column, move down to the next column.
                left += 1
                dir = 0


## in and out spiral; not complete....
def image2gcode_spiral_cube2(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var,wall_thickness, offset_ON, offset_OFF):
    black = 0
    white = 255
    img_list = []
    for image in image_list:
        img = cv2.imread(image, 0)
        img = cv2.flip(img, 0)  # flip over y-axis
        img_list.append(img)  # converts images to pixels

    img_shape = img_list[0].shape  # finds width and height of image (will use the first image in the last)
    height = img_shape[0]
    width = img_shape[1]

    num_layers = int(height)

    ### This section creates the spiral print path
    if wall_thickness == 'solid':
        current_length = fil_width
    else:
        current_length = width - (2 * wall_thickness - 1)

    p_list_A = []  # relative coordinate
    dir_list_A = []  # direction of nozzle
    face_list_A = []  # face on the cube

    # for wall in range(wall_thickness):
    while current_length < width:

        if current_length == fil_width:
            p_start = [current_length, 0]
            p_list_A.append(p_start)
            dir_list_A.append('East')  # direction of nozzle
            face_list_A.append('South')  # face on the cube

        # N -> W -> S -> E (A layers go outward)
        p1 = [0, current_length]  # NORTH

        current_length += fil_width

        p2 = [-current_length, 0]  # WEST
        p3 = [0, -current_length]  # SOUTH

        if current_length < width:
            current_length += fil_width

        p4 = [current_length, 0]  # EAST

        p_list_A.append(p1)
        dir_list_A.append('North')  # direction of nozzle
        face_list_A.append('East')  # face on the cube

        p_list_A.append(p2)
        dir_list_A.append('West')
        face_list_A.append('North')

        p_list_A.append(p3)
        dir_list_A.append('South')
        face_list_A.append('West')

        p_list_A.append(p4)
        dir_list_A.append('East')
        face_list_A.append('South')

    # B layers go inwards
    p_list_B = list(reversed(p_list_A))
    for i in range(len(p_list_B)):
        p_list_B[i] = list(reversed(p_list_B[i]))

    dir_list_B = dir_list_A
    face_list_B = face_list_A

    with open('----testingNewSpiral.txt----','w') as f:
        f.write('G91')
        for layer in range(num_layers):
            f.write("\nG1 Z1")
            if (layer+1)%2 != 0: # odd
                for i in range(len(p_list_A)):
                    f.write('\nG1 X' + str(p_list_A[i][0]) + ' Y' + str(p_list_A[i][1]))
            else:
                for i in range(len(p_list_B)):
                    f.write('\nG1 X' + str(p_list_B[i][0]) + ' Y' + str(p_list_B[i][1]))




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # image1 = 'Heart50x50.png'#'checkerboard_30x30pix.png' #'Heart50x50.png'#flask_30pix.png'  # 'temp_aaron.png'#'temp_heart.png'
    # image2 = 'Heart50x50.png'#'checkerboard_30x30pix.png' #'Heart50x50.png'#happy_chemistry_spill_30pix.png'  # 'temp_smiley.png'
    # image3 = 'Heart50x50.png'#'checkerboard_30x30pix.png' #'Heart50x50.png'#'happy_chemistry_spill_30pix.png'  # 'temp_heart.png'
    # image4 = 'Heart50x50.png'#'checkerboard_30x30pix.png' #'Heart50x50.png' #'flask_30pix.png'  # 'temp_sarah_waz.png'
    image1 = 'checkerboard_30x30pix.png' #'Heart50x50.png'#flask_30pix.png'  # 'temp_aaron.png'#'temp_heart.png'
    image2 = 'checkerboard_30x30pix.png' #'Heart50x50.png'#happy_chemistry_spill_30pix.png'  # 'temp_smiley.png'
    image3 = 'checkerboard_30x30pix.png' #'Heart50x50.png'#'happy_chemistry_spill_30pix.png'  # 'temp_heart.png'
    image4 = 'checkerboard_30x30pix.png' #'Heart50x50.png' #'flask_30pix.png'  # 'temp_sarah_waz.png'

    txt_export = '----testingOFFSET----.txt'

    image_bottom = 'flask_30pix.png'
    image_top = 'happy_chemistry_spill_30pix.png'

    ## To view in g-code simulator (https://nraynaud.github.io/webgcode/):
    visualize_ON = True

    ## Geometry
    wall_thickness = 'solid'  # OPTIONS: a number or 'solid'
    fil_width = 1  # filament spacing
    z_height = 1  # layer height
    z_var = "D"  # for use in aerotech

    ## Offset compensation
    offset_ON = 5
    offset_OFF = 5

    ## Valve Toggle
    #### Toggle ON (grouped by face of cube)
    dirNorth_faceEast_ON = 'NE ON'
    dirSouth_faceEast_ON = 'SE ON'

    dirNorth_faceWest_ON = 'NW ON'
    dirSouth_faceWest_ON = 'SW ON'

    dirWest_faceNorth_ON = 'WN ON'
    dirEast_faceNorth_ON = 'EN ON'

    dirWest_faceSouth_ON = 'WS ON'
    dirEast_faceSouth_ON = 'ES ON'

    #### Toggle OFF (grouped by face of cube)
    dirNorth_faceEast_OFF = 'NE OFF'
    dirSouth_faceEast_OFF = 'SE OFF'

    dirNorth_faceWest_OFF = 'NW OFF'
    dirSouth_faceWest_OFF = 'SW OFF'

    dirWest_faceNorth_OFF = 'WN OFF'
    dirEast_faceNorth_OFF = 'EN OFF'

    dirWest_faceSouth_OFF = 'WS OFF'
    dirEast_faceSouth_OFF = 'ES OFF'

    ##################################################################################################
    toggle_ON_list = [
        dirNorth_faceEast_ON,
        dirNorth_faceWest_ON,
        dirSouth_faceEast_ON,
        dirSouth_faceWest_ON,
        dirWest_faceNorth_ON,
        dirWest_faceSouth_ON,
        dirEast_faceNorth_ON,
        dirEast_faceSouth_ON
    ]

    toggle_OFF_list = [
        dirNorth_faceEast_OFF,
        dirNorth_faceWest_OFF,
        dirSouth_faceEast_OFF,
        dirSouth_faceWest_OFF,
        dirWest_faceNorth_OFF,
        dirWest_faceSouth_OFF,
        dirEast_faceNorth_OFF,
        dirEast_faceSouth_OFF
    ]

    image_list = [image1, image2, image3, image4]

    output = image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, wall_thickness, offset_ON, offset_OFF)
    G_list = output[0]
    var_list = output[1]
    dist_list = output[2]
    command_list = output[3]

    #image2gcode_spiral_cube2(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, wall_thickness, offset_ON, offset_OFF)

    print(dist_list)
    print(command_list)
    print('--------------------')
    offset = 2
    for i in range(len(G_list)):
        if command_list[i] != '':  # if there is a command associated with the distance

            offset_dist = abs(dist_list[i]) - offset
            add_offset = offset
            if dist_list[i] < 0:
                offset_dist = -offset_dist
                add_offset = -offset

            dist_list[i] = offset_dist

            dist_list[i+1] = dist_list[i+1] + add_offset

            # if offset_dist >= 0:
            #
            #     if dist_list[i] < 0:
            #         offset_dist = -offset_dist
            #
            #     dist_list[i] = offset_dist
            #
            #     if var_list[i] == var_list[i+1]:
            #         if dist_list[i+1] < 0:
            #             offset = -offset
            #
            #         dist_list[i+1] = dist_list[i+1] + offset
            #
            # else:
            #     count = 0
            #     while offset_dist < 0:
            #         offset_new = abs(offset_dist)
            #         count += 1
            #         offset_dist = abs(dist_list[i-count]) - offset_new
            #
            #     if dist_list[i-count] < 0:
            #         offset_dist = - offset_dist
            #
            #     if var_list[i] == var_list[i+1]:
            #         dist_list[i + 1] = abs(dist_list[i + 1]) + abs(dist_list[i])
            #         if dist_list[i+1] < 0:
            #             dist_list[i + 1] = - dist_list[i+1]
            #
            #     dist_list[i-count] = dist_list[i-count] + offset
            #
            #     dist_list.insert(i - (count +1), offset_dist)
            #     G_list.insert(i - (count +1), G_list[i-count])
            #     command_list.insert(i - (count +1), command_list[i])
            #
            #     dist_list[i] = 0
            #     command_list[i] = ''







    with open(txt_export, 'w') as f:
        f.write('G91\n')
        for i in range(len(G_list)):
            if var_list[i] == 'Z':
                f.write('\n------ new layer')
            f.write('\n' + str(G_list[i]) + ' ' + str(var_list[i]) + str(dist_list[i]))
            f.write('\n' + command_list[i])



