import cv2
import numpy as np

'''NOTES
* all images must be the same size
* 1 pixel = 1 mm
'''


def image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var,wall_thickness, offset):
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

    '''This section creates the spiral print path'''
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

    '''This section makes sure the final layer does not have dollop in the center'''
    if height % 2 != 0:  # if the height is an odd number, starts  the print on the inner walls
        p_list_odd = p_list_A
        dir_list_odd = dir_list_A
        face_list_odd = face_list_A

        p_list_even = p_list_B
        dir_list_even = dir_list_B
        face_list_even = face_list_B

        outer_edge_list_odd = p_list_odd[-4:]

        outer_edge_list_even = p_list_even[0:4]

    else:  # if even, starts the print on the outer walls
        p_list_odd = p_list_B
        dir_list_odd = dir_list_B
        face_list_odd = face_list_B

        p_list_even = p_list_A
        dir_list_even = dir_list_A
        face_list_even = face_list_A

        outer_edge_list_odd = p_list_odd[0:4]

        outer_edge_list_even = p_list_even[-4:]

    '''This section creates the final print path that will be used'''


    z = z_height
    prev_pixel = ''


    if visualize_ON == True:
        z_var = "Z"

    ### when the wall thickness is > 1, the offset for the first image (east face) occurs on an inner wall
    if wall_thickness != 1:
        internal_offset = p_list_A[-5]
    else:
        internal_offset = []

    dist_list = []
    var_list = []
    command_list = []
    G_list = []

    print('G91')
    for layer in range(num_layers):
        print(';---LAYER-----', layer + 1)
        if (layer + 1) % 2 != 0:
            p_list = p_list_odd
            face_list = face_list_odd
            dir_list = dir_list_odd
            outer_edge_list = outer_edge_list_odd

        else:
            p_list = p_list_even
            face_list = face_list_even
            dir_list = dir_list_even
            outer_edge_list = outer_edge_list_even

        print(';---outer edge---', outer_edge_list)

        for coordinates in range(len(p_list)):

            if p_list[coordinates] not in outer_edge_list and p_list[coordinates] != internal_offset:
                print('G1 X' + str(p_list[coordinates][0]) + ' Y' + str(p_list[coordinates][1]))

            else:
                current_face = face_list[coordinates]
                current_dir = dir_list[coordinates]
                print(';---current face----', current_face)
                print(';---current dir----', current_dir)

                ### This section defines the print direction based on the face_list and the dir_list
                if current_dir == 'North':
                    variable = 'Y'
                    sign = 1

                if current_dir == 'South':
                    variable = 'Y'
                    sign = -1

                if current_dir == 'East':
                    variable = 'X'
                    sign = 1

                if current_dir == 'West':
                    variable = 'X'
                    sign = -1

                current_distance = 0

                ### This section defines when each pixel will be printed (includes offets)
                if p_list[coordinates] == internal_offset:  # this takes care of the offset for the first pixels in the 1st image (which need to be turned on during an internal wall)

                    img_pix_append = img_list[0][layer][0:offset]  # takes first n pixels of image 1 to turn on early
                    for dist in p_list[coordinates]:
                        if dist != 0:
                            distance = abs(dist) - offset
                            img_pix_current = []
                            for num in range(distance):
                                img_pix_current = np.append(img_pix_current, white)

                    prev_pixel = white

                    image_number = 0
                    append_image_number = 0

                elif current_face == 'East':  # Image 1, nozzle moving North or South
                    image_number = 0
                    current_image_pixels = img_list[image_number][layer]
                    current_image_pixels = current_image_pixels[
                                           1:]  # deletes first pixel because it is replaced by +Z movement

                    if current_dir == 'North':
                        append_image_number = image_number + 1
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels

                        if wall_thickness == 1 and layer == 0:
                            img_pix_current = current_image_pixels

                        next_image_pixels = img_list[append_image_number][layer]
                        img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image



                    else:
                        append_image_number = image_number

                        current_image_pixels = np.flip(
                            current_image_pixels)  # flips orders of pixels because print direction is "negative"
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels

                        img_pix_append = []
                        for o in range(offset):  # adds n white pixels
                            img_pix_append = np.append(img_pix_append, white)

                        if wall_thickness == 1:
                            next_image_pixels = img_list[append_image_number][layer + 1]
                            img_pix_append = next_image_pixels[0:offset]

                        if wall_thickness == 'solid' or wall_thickness > 1:
                            if layer != len(img_list[image_number]) - 1:  # if not on the last layer
                                next_image_pixels = img_list[append_image_number][layer + 1]
                                img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image
                            else:
                                img_pix_append = []
                                for o in range(offset):  # adds n white pixels
                                    img_pix_append.append(white)



                elif current_face == 'North':  # Image 2, nozzle moving East or West
                    image_number = 1
                    current_image_pixels = img_list[image_number][layer]
                    if current_dir == 'West':
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels
                        append_image_number = image_number + 1
                        next_image_pixels = img_list[append_image_number][layer]
                        img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image



                    else:
                        current_image_pixels = np.flip(
                            current_image_pixels)  # flips orders of pixels because print direction is "negative"
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels
                        append_image_number = image_number - 1
                        next_image_pixels = img_list[append_image_number][layer]
                        next_image_pixels = np.flip(next_image_pixels)
                        img_pix_append = next_image_pixels[0:offset]




                elif current_face == 'West':  # Image 3, nozzle moving North or South
                    image_number = 2
                    current_image_pixels = img_list[image_number][layer]
                    if current_dir == 'South':
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels
                        append_image_number = image_number + 1
                        next_image_pixels = img_list[append_image_number][layer]
                        img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image



                    else:
                        current_image_pixels = np.flip(
                            current_image_pixels)  # flips orders of pixels because print direction is "negative"
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels
                        append_image_number = image_number - 1
                        next_image_pixels = img_list[append_image_number][layer]
                        next_image_pixels = np.flip(next_image_pixels)
                        img_pix_append = next_image_pixels[0:offset]



                elif current_face == 'South':  # Image 4, nozzle moving East or West
                    image_number = 3
                    current_image_pixels = img_list[image_number][layer]

                    if current_dir == 'East':
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels
                        append_image_number = image_number

                        if layer != len(img_list[image_number]) - 1:
                            next_image_pixels = img_list[append_image_number][layer + 1]
                            next_image_pixels = np.flip(next_image_pixels)
                            img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image
                        else:
                            img_pix_append = []
                            for o in range(offset):  # adds n white pixels
                                img_pix_append.append(white)

                    else:
                        current_image_pixels = np.flip(
                            current_image_pixels)  # flips orders of pixels because print direction is "negative"
                        if layer == 0:
                            img_pix_current = current_image_pixels
                        else:
                            img_pix_current = current_image_pixels[offset:]  # deletes first n pixels

                        append_image_number = image_number - 1
                        next_image_pixels = img_list[append_image_number][layer]
                        next_image_pixels = np.flip(next_image_pixels)
                        img_pix_append = next_image_pixels[0:offset]

                current_image_valve_ON = toggle_ON_list[image_number]
                current_image_valve_OFF = toggle_OFF_list[image_number]

                append_image_valve_ON = toggle_ON_list[append_image_number]
                append_image_valve_OFF = toggle_OFF_list[append_image_number]

                valve_ON_list = []
                valve_OFF_list = []
                for elem in img_pix_current:
                    valve_ON_list.append(current_image_valve_ON)
                    valve_OFF_list.append(current_image_valve_OFF)

                for elem in img_pix_append:
                    valve_ON_list.append(append_image_valve_ON)
                    valve_OFF_list.append(append_image_valve_OFF)

                current_img = np.append(img_pix_current, img_pix_append)  # part of next image starts at end


                ##### This section determines where to turn pixels on and off in the print
                for pix in range(len(current_img)):
                    pixel = current_img[pix]
                    valve_ON = valve_ON_list[pix]
                    valve_OFF = valve_OFF_list[pix]

                    if pixel != white:
                        pixel = black

                    if prev_pixel != pixel:
                        if pixel == black:
                            if current_distance != 0:
                                print('G1 ' + str(variable) + str(sign * (current_distance)))
                            print(valve_ON)
                            valve_ON_flag = True


                        elif pixel != black and prev_pixel != '':
                            if current_distance != 0:
                                if visualize_ON == True:
                                    print('G0 ' + str(variable) + str(sign * (current_distance)))

                                else:
                                    print('G1 ' + str(variable) + str(sign * (current_distance)))

                            print(valve_OFF)
                            valve_ON_flag = False

                        current_distance = 0

                    current_distance += 1
                    prev_pixel = pixel

                    if pix == len(img_pix_current) - 1 and valve_ON_flag == True:
                        if pixel == white or visualize_ON == False:
                            print('G1 ' + str(variable) + str(sign * (current_distance)))
                        else:
                            print('G0 ' + str(variable) + str(sign * (current_distance)))

                        print('---here')
                        print(valve_OFF)
                        prev_pixel = ''
                        current_distance = 0

                if pixel == white or visualize_ON == False:
                    print('G1 ' + str(variable) + str(sign * (current_distance)))
                else:
                    print('G0 ' + str(variable) + str(sign * (current_distance)))


        print('G1 ' + str(z_var) + str(z))

    return G_list, var_list, dist_list, command_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    image1 = 'checkerboard_30x30pix.png'  # 'Heart50x50.png'#flask_30pix.png'  # 'temp_aaron.png'#'temp_heart.png'
    image2 = 'checkerboard_invert_30x30pix.png'  # 'checkerboard_invert_30x30pix.png' #'Heart50x50.png'#happy_chemistry_spill_30pix.png'  # 'temp_smiley.png'
    image3 = 'checkerboard_30x30pix.png'  # 'Heart50x50.png'#'happy_chemistry_spill_30pix.png'  # 'temp_heart.png'
    image4 = 'checkerboard_invert_30x30pix.png'  # 'checkerboard_invert_30x30pix.png' #'Heart50x50.png' #'flask_30pix.png'  # 'temp_sarah_waz.png'

    txt_export = '----testingOFFSET----.txt'


    ## To view in g-code simulator (https://nraynaud.github.io/webgcode/):
    visualize_ON = False

    ## Geometry
    wall_thickness = 2  # 'solid'  # OPTIONS: a number or 'solid'
    fil_width = 1  # filament spacing
    z_height = 1  # layer height
    z_var = "A"  # for use in aerotech

    ## Offset compensation
    offset = 2

    ## Valve Toggle
    #### Toggle ON (grouped by face of cube)
    faceEast_ON = '$OutBits[$Valve4] = 1'

    faceWest_ON = '$OutBits[$Valve2] = 1'

    faceNorth_ON = '$OutBits[$Valve3] = 1'

    faceSouth_ON = '$OutBits[$Valve1] = 1'

    #### Toggle OFF (grouped by face of cube)
    faceEast_OFF = '$OutBits[$Valve4] = 0'

    faceWest_OFF = '$OutBits[$Valve2] = 0'

    faceNorth_OFF = '$OutBits[$Valve3] = 0'

    faceSouth_OFF = '$OutBits[$Valve1] = 0'

    ##################################################################################################
    toggle_ON_list = [
        faceEast_ON,
        faceNorth_ON,
        faceWest_ON,
        faceSouth_ON,
    ]

    toggle_OFF_list = [
        faceEast_OFF,
        faceNorth_OFF,
        faceWest_OFF,
        faceSouth_OFF,

    ]

    image_list = [image1, image2, image3, image4]

    output = image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height,
                                     z_var, wall_thickness, offset)
