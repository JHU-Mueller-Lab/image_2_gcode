import cv2
import numpy as np

def image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var,wall_thickness, offset, offset_large):
    black = 0
    white = 255
    img_list = []
    scale_factor = fil_width
    count = 0

    import sys
    if offset/scale_factor != int(offset/scale_factor):
        print('INPUT ERROR: offset/fil_width must be an integer value but is currently ', offset/scale_factor, '\nChange inputs so that offset/fil_width is an integer.')
        sys.exit()
    if offset_large/scale_factor != int(offset_large/scale_factor):
        print('INPUT ERROR: offset_large/fil_width must be an integer value but is currently ', offset_large/scale_factor, '\nChange inputs so that offset/fil_width is an integer.')
        sys.exit()

    offset = int(offset / scale_factor)
    offset_large = int(offset_large / scale_factor)

    if offset > offset_large:
        print('INPUT ERROR: offset_large must be greater than or equal to the offset.', '\nChange inputs so that offset_large >= offset.')
        sys.exit()



    for image in image_list:
        img = cv2.imread(image, 0)
        img = cv2.flip(img, 0)  # flip over y-axis
        # img = cv2.resize(img, None, fx=1 / scale_x, fy=1 / scale_y, interpolation=cv2.INTER_LINEAR)

        for i in range(len(img)):
            for j in range(len(img[i])):
                pixel = img[i][j]
                if abs(pixel - 0) < abs(pixel - 255):
                    img[i][j] = 0
                else:
                    img[i][j] = 255
            cv2.imwrite('CheckImage_' + str(count) + '.png', img)

        img_list.append(img)  # converts images to pixels
        count += 1

    img_shape = img_list[0].shape  # finds width and height of image (will use the first image in the last)
    height = img_shape[0]
    width = img_shape[1]

    num_layers = int(height)

    '''This section creates the spiral print path'''
    if wall_thickness == 'solid':
        current_length = 1
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

        current_length += 1  # fil_width

        p2 = [-current_length, 0]  # WEST
        p3 = [0, -current_length]  # SOUTH

        if current_length < width:
            current_length += 1  # fil_width

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

        start_direction = 1

        start_sequence = [0, 1, 2, 3, 4]

    else:  # if even, starts the print on the outer walls
        p_list_odd = p_list_B
        dir_list_odd = dir_list_B
        face_list_odd = face_list_B

        p_list_even = p_list_A
        dir_list_even = dir_list_A
        face_list_even = face_list_A

        outer_edge_list_odd = p_list_odd[0:4]

        outer_edge_list_even = p_list_even[-4:]

        start_direction = -1

        start_sequence = [4, 3, 2, 1, 0]

    ### when the wall thickness is > 1, the offset for the first image (east face) occurs on an inner wall
    if wall_thickness != 1:
        internal_offset = p_list_A[-5]
    else:
        internal_offset = []

    ### create blank image for internal wall.
    for coordinate in internal_offset:
        if coordinate != 0:
            length_of_internal_wall = abs(coordinate)

    internal_wall_image = [[white for col in range(length_of_internal_wall)] for row in range(num_layers)]


    img_list.insert(0, internal_wall_image)
    img_list.append(img_list[4])


    toggle_ON_list.insert(0, '')
    toggle_OFF_list.insert(0, '')

    toggle_ON_list.append(toggle_ON_list[4])
    toggle_OFF_list.append(toggle_OFF_list[4])

    first_black_pixel_dict = {}
    relocate_first_black_pixel_dict = {}
    row_to_start_early_dict = {}
    row_to_start_on_correct_face_dict = {}
    first_black_pixel_row_list = []
    relocate_first_black_pixel_list = []
    row_to_start_on_earlier_face_list = []
    row_to_start_on_correct_face_list = []

    '''find when the first black pixel occurs'''
    for img_number in range(len(img_list)): # for each image

        current_img = img_list[img_number]
        offset_initial = offset_large
        # if img_number != 0:
        #     cv2.imwrite('CheckImage_' + str(img_number) + '.png', current_img)

        for row_number in range(len(current_img)): # for each row in each image
            first_black_pixel_flag = False
            current_row = list(current_img[row_number])

            if img_number == 1:
                current_row = list(current_img[row_number][1:]) # deletes first pixel because it is taken up by Z

            if (row_number+1)%2 != 0 and start_direction == -1: # reverses odd layers
                    current_row = list(np.flip(current_row))
                    if img_number == 5:
                        offset_initial = offset

            elif (row_number + 1)% 2 == 0 and start_direction == 1:  # reverses even layers
                    current_row = list(np.flip(current_row))

                    if img_number == 5:
                        offset_initial = offset

            for pixel_number in range(len(current_row)): # for each pixel in each row
                current_pixel = current_row[pixel_number]
                if current_pixel == black and first_black_pixel_flag == False:
                    first_black_pixel = pixel_number
                    # first_black_pixel_row_list.append(first_black_pixel)
                    first_black_pixel_flag = True

            if first_black_pixel_flag == False:
                first_black_pixel = None


            if first_black_pixel == None:
                row_to_start_on_earlier_face = current_row
                row_to_start_on_correct_face = current_row
                #print(img_number, row_number, 'no offset',  len(current_row))

            else:
                row_to_start_on_earlier_face = [white for col in range(len(current_row))] # list of white pixels in size of the current row
                relocate_first_black_pixel = first_black_pixel - offset_initial

                relocate_first_black_pixel_list.append(relocate_first_black_pixel)
                if relocate_first_black_pixel < 0:
                    row_to_start_on_earlier_face[relocate_first_black_pixel] = black
                    add_additional_black_pix = relocate_first_black_pixel + 1
                    extra_black_pix_added = 0
                    while add_additional_black_pix <= -1:
                        row_to_start_on_earlier_face[add_additional_black_pix] = black
                        add_additional_black_pix += 1
                        extra_black_pix_added += 1

                    more_black_pix_to_add = (offset_initial - offset) - extra_black_pix_added

                    row_to_start_on_correct_face = current_row[(offset_initial - offset):]  # delete first n pixels for offset

                    if more_black_pix_to_add > 0:
                        for i in range(more_black_pix_to_add):
                            row_to_start_on_correct_face.insert(0, black)  # add more black to beginning

                    while len(row_to_start_on_correct_face) < len(current_row):
                        row_to_start_on_correct_face.append(white)  # add white to end

                else:

                    more_black_pix_to_add = offset_initial - offset

                    row_to_start_on_correct_face = current_row[offset:]
                    row_to_start_on_correct_face[offset_initial - 1] = black

                    for i in range(more_black_pix_to_add):
                        row_to_start_on_correct_face[offset_initial + i] = black #.insert(0, black)  # add more black to beginning

                    for i in range(offset):
                        row_to_start_on_correct_face.append(white)  # add white to end


            row_to_start_on_earlier_face_list.append(row_to_start_on_earlier_face)
            row_to_start_on_correct_face_list.append(row_to_start_on_correct_face)


        row_to_start_early_dict[img_number] = row_to_start_on_earlier_face_list
        row_to_start_on_correct_face_dict[img_number] = row_to_start_on_correct_face_list


        row_to_start_on_earlier_face_list = []
        row_to_start_on_correct_face_list = []



    '''This section creates the final print path that will be used'''
    z = z_height
    prev_pixels = ['', '']


    if visualize_ON == True:
        z_var = "Z"

    print('G91')
    for layer in range(num_layers):
        if (layer + 1) % 2 != 0:  # odd rows
            sequence = start_sequence*1

        else:
            sequence = start_sequence * -1

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
                print('G1 X' + str(p_list[coordinates][0]*scale_factor) + ' Y' + str(p_list[coordinates][1]*scale_factor))

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
                offset_layer = layer

                ### This section defines when each pixel will be printed (includes offets)
                if p_list[coordinates] == internal_offset:  # this takes care of the offset for the first pixels in the 1st image (which need to be turned on during an internal wall)
                    current_image_number = 0
                    next_image_number = 1

                elif current_face == 'East':  # Image 1, nozzle moving North or South
                    if current_dir == 'North':
                        current_image_number = 1
                        next_image_number = 2
                    else:
                        current_image_number = 1
                        next_image_number = 0

                elif current_face == 'North':  # Image 2, nozzle moving West or East
                    if current_dir == 'West':
                        current_image_number = 2
                        next_image_number = 3
                    else:
                        current_image_number = 2
                        next_image_number = 1


                elif current_face == 'West':  # Image 3, nozzle moving West or East
                    if current_dir == 'South':
                        current_image_number = 3
                        next_image_number = 4
                    else:
                        current_image_number = 3
                        next_image_number = 2


                elif current_face == 'South':  # Image 4, nozzle moving West or East

                    if current_dir == 'East':
                        current_image_number = 4
                        next_image_number = 5  # this is the same image as 4
                        offset_layer = layer + 1

                    else:
                        current_image_number = 4
                        next_image_number = 3

                current_image = row_to_start_on_correct_face_dict[current_image_number][layer]


                if (layer+1) != num_layers: # last layer
                    next_image = row_to_start_early_dict[next_image_number][offset_layer]
                else:
                    next_image = [white for col in range(len(current_image))]

                if len(current_image) != len(next_image):
                    print('---here', current_image_number, next_image_number, len(current_image), len(next_image))

                count = 0
                while len(current_image) < len(next_image): # make the images the same size
                    next_image = next_image[count:]
                    count += 1

                while len(current_image) > len(next_image):  # make the images the same size
                    next_image.insert(0, white)


                pixel_list = [current_image, next_image]

                valve_ON_list = [toggle_ON_list[current_image_number], toggle_ON_list[next_image_number]]
                valve_OFF_list = [toggle_OFF_list[current_image_number], toggle_OFF_list[next_image_number]]


                # print('pixel_list1 =', pixel_list[0])
                # print('pixel_list2 =', pixel_list[1])
                # print('image_number_list =', current_image, next_image)

                ##### This section determines where to turn pixels on and off in the print
                for pix in range(len(current_image)):
                    pixels = [pixel_list[0][pix],  pixel_list[1][pix]]

                    for pixel_count in range(len(pixels)):
                        pixel = pixels[pixel_count]
                        prev_pixel = prev_pixels[pixel_count]
                        if prev_pixel != pixel:
                            if pixel == black:
                                if current_distance != 0:
                                    print('G1 ' + str(variable) + str(sign * (current_distance*scale_factor)))

                                print(valve_ON_list[pixel_count])


                            elif pixel != black and prev_pixel != '':
                                if current_distance != 0:
                                    if visualize_ON == True:
                                        print('G0 ' + str(variable) + str(sign * (current_distance*scale_factor)))

                                    else:
                                        print('G1 ' + str(variable) + str(sign * (current_distance*scale_factor)))

                                print(valve_OFF_list[pixel_count])

                            current_distance = 0

                    current_distance += 1
                    prev_pixels = [pixel_list[0][pix],  pixel_list[1][pix]]

                    if pix == len(current_image) - 1:
                        if pixels[0] == white or visualize_ON == False:
                            print('G1 ' + str(variable) + str(sign * (current_distance*scale_factor)))
                        else:
                            print('G0 ' + str(variable) + str(sign * (current_distance*scale_factor)))

                        if next_image_number != 4:
                            print(valve_OFF_list[0])

                        prev_pixels = [pixel_list[0][pix],  '']
                        current_distance = 0

                if pixels[0] == white or visualize_ON == False:
                    if current_distance != 0:
                        print('G1 ' + str(variable) + str(sign * (current_distance*scale_factor)))
                else:
                    if current_distance != 0:
                        print('G0 ' + str(variable) + str(sign * (current_distance*scale_factor)))


        print('G1 ' + str(z_var) + str(z))

    for elem in valve_OFF_list:
        print(elem)
    return #G_list, var_list, dist_list, command_list

'''NOTES
- creates a spiral print path with images that wrap around only the outside walls
- all images must be the same size
- visualize_ON = True shows the images in red by making black sections into G0 moves; to make a printable gcode, make sure to visualize_ON = False
- you can scale your image using the fil_width. if fil_width < 1, the images (and cube) will shrink. if fil_width > 1, the images will be enlarged. 
- make sure the offsets are an even factor of the fil_width (e.g., offset/fil_width = integar)
- to account for backflow, you can define a larger offset length for when the layers have not been on for a long time.  
'''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    image1 = 'SerpentHead_28px_V2.png'  # 'Heart50x50.png'#flask_30pix.png'  # 'temp_aaron.png'#'temp_heart.png'
    image2 = 'SerpentBody_28px_V2.png'  # 'checkerboard_invert_30x30pix.png' #'Heart50x50.png'#happy_chemistry_spill_30pix.png'  # 'temp_smiley.png'
    image3 = 'SerpentBody_28px_V2.png'  # 'Heart50x50.png'#'happy_chemistry_spill_30pix.png'  # 'temp_heart.png'
    image4 = 'SerpentTail_28px_V2.png'  # 'checkerboard_invert_30x30pix.png' #'Heart50x50.png' #'flask_30pix.png'  # 'temp_sarah_waz.png'

    ## To view in g-code simulator (https://nraynaud.github.io/webgcode/):
    visualize_ON = True

    ## Geometry
    wall_thickness = 2 # 'solid'  # OPTIONS: a number or 'solid' # must be greater than 1
    fil_width = 1 #filament spacing
    z_height = fil_width # layer height
    z_var = "A"  # for use in aerotech

    ## Offset compensation
    offset = 1 #this offset is used when materials have been on for an extended period of time. (offset/fil_width = integar)
    offset_large = 3 # this is the offset used when materials have been turned off too long and accounts for backflow. (offset_large/fil_width = integar)

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

    output = image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height,z_var, wall_thickness, offset, offset_large)