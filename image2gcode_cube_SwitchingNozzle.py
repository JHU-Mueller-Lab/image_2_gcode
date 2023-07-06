import cv2
import numpy as np

def setpress(pressure):
    # IMPORTS
    from codecs import encode
    from textwrap import wrap

    pressure = str(pressure * 10)
    length = len(pressure)
    while length < 4:
        pressure = "0" + pressure
        length = len(pressure)

    commandc = bytes(('08PS  ' + pressure), "utf-8")

    # FIND CHECKSUM
    startc = b'\x05\x02'
    endc = b'\x03'

    hexcommand = encode(commandc, "hex")  # encode should turn this into a hex rather than ascii

    hexcommand = hexcommand.decode("utf-8")  # decode should turn this into a string object rather than a bytes object

    ####format for arduino#####
    format_command = str(hexcommand)
    format_command = '\\x'.join(format_command[i:i + 2] for i in range(0, len(format_command), 2))
    format_command = '\\x' + format_command
    ##########################

    hexcommand = wrap(hexcommand,
                      2)  # wrap should split the string into a horizontal array of strings of 2 characters each

    # GETTING THE 8 BIT 2'S COMPLEMENT
    decimalsum = 0
    for i in hexcommand:  # get the decimal sum of the hex command
        decimalsum = decimalsum + int(i, 16)
    checksum = decimalsum % 256  # get the remainder of the decimal sum
    checksum = bin(checksum)  # turn into binary
    checksum = checksum[2:]  # checksum is a string
    while len(checksum) < 8:  # checksum must represents 8 bits of information
        checksum = "0" + checksum
    invert = ""
    for i in checksum:  # binary sum must be inverted
        if i == '0':
            invert = invert + "1"
        else:
            invert = invert + "0"
    invert = int(invert, 2)  # binary sum turned into decimal form
    invert = invert + 1
    # CHECKSUM HAS BEEN RETRIEVED IN DECIMAL FORM
    checksum = invert
    checksum = hex(checksum)  # checksum is in the format "0x##"
    # CHECKSUM IS NOW IN ASCII FORM, don't be mislead by the hex function
    checksum = checksum[2:]
    checksumarray = []
    for i in checksum:  # must get alphabetical characters in uppercase for ascii to hex conversion
        if i.isalpha():
            i = i.upper()
            checksumarray.append(i)
        else:
            checksumarray.append(i)
    checksum = ""
    for i in checksumarray:
        checksum = checksum + i
    # checksum is a string.
    checksum = bytes(checksum, 'ascii')

    ####format for arduino#####
    hexchecksum = encode(checksum, 'hex')
    hexchecksum = hexchecksum.decode("utf-8")  # decode should turn this into a string object rather than a bytes object
    format_checksum = str(hexchecksum)  # format for arduino
    format_checksum = '\\x'.join(format_checksum[i:i + 2] for i in range(0, len(format_checksum), 2))
    format_checksum = '\\x' + format_checksum

    # SENDING OUT THE COMMAND
    ##format for arduino####
    finalcommand = ("\\x05\\x02") + format_command + format_checksum + str("\\x03")
    finalcommand = finalcommand.strip('\r').strip('\n')
    finalcommand = "b'" + finalcommand + "'"
    return finalcommand
def togglepress():
    # IMPORTS
    toggle = str("b'\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03'")
    return toggle


'''NOTES
* all images must be the same size
* 1 pixel = 1 mm
'''

def image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var,wall_thickness, offset):
    black = 0
    white = 255
    img_list = []
    scale_factor = fil_width
    count = 0
    offset = int(offset/fil_width)

    for image in image_list:
        img = cv2.imread(image, 0)
        img = cv2.flip(img, 0)  # flip over y-axis

        #img = cv2.resize(img, None, fx=1 / scale_x, fy=1 / scale_y, interpolation=cv2.INTER_LINEAR)

        for i in range(len(img)):
            # for j in range(len(img[i])):
            #         pixel = img[i][j]
            #         if abs(pixel - 0) < abs(pixel - 255):
            #             img[i][j] = 0
            #         else:
            #             img[i][j] = 255
            cv2.imwrite('CheckImage_' +str(count) +'.png', img)

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

        current_length += 1#fil_width

        p2 = [-current_length, 0]  # WEST
        p3 = [0, -current_length]  # SOUTH

        if current_length < width:
            current_length += 1#fil_width

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

    white_ON_flag = False
    black_ON_flag = False
    first_toggle = True
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
                if coordinates == 0:
                    ON_color = 0
                    print(toggle_ON_list[0])

                if ON_color != 0:
                    print(toggle_ON_list[0])
                    print(toggle_OFF_list[ON_color])
                    ON_color = 0

                    # black_ON_flag = False
                    # white_ON_flag = True
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


                ### This section defines when each pixel will be printed (includes offets)
                if p_list[coordinates] == internal_offset:  # this takes care of the offset for the first pixels in the 1st image (which need to be turned on during an internal wall)

                    if current_dir == 'East':
                        img_pix_append = img_list[0][layer][0:offset]  # takes first n pixels of image 1 to turn on early
                        for dist in p_list[coordinates]:
                            if dist != 0:
                                distance = abs(dist) - offset
                                img_pix_current = []
                                for num in range(int(distance)):
                                    img_pix_current = np.append(img_pix_current, white)

                    else:
                        for dist in p_list[coordinates]:
                            if dist != 0:
                                distance = abs(dist)/2
                                img_pix_current = []
                                for num in range(int(distance)):
                                    img_pix_current = np.append(img_pix_current, white)

                        img_pix_append = img_pix_current
                    prev_pixel = white

                    image_number = 0
                    append_image_number = 0

                elif current_face == 'East':  # Image 1, nozzle moving North or South
                    image_number = 0
                    current_image_pixels = img_list[image_number][layer]
                    current_image_pixels = current_image_pixels[1:]  # deletes first pixel because it is replaced by +Z movement

                    if current_dir == 'North':
                        append_image_number = image_number + 1
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels

                        if wall_thickness == 1 and layer == 0:
                            img_pix_current = current_image_pixels

                        next_image_pixels = img_list[append_image_number][layer]
                        img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image



                    else:
                        append_image_number = image_number

                        current_image_pixels = np.flip(current_image_pixels)  # flips orders of pixels because print direction is "negative"
                        img_pix_current = current_image_pixels[offset:]  # deletes first n pixels

                        img_pix_append = []
                        for o in range(offset):  # adds n white pixels
                            img_pix_append = np.append(img_pix_append, white)

                        if wall_thickness == 1:
                            next_image_pixels = img_list[append_image_number][layer + 1]
                            img_pix_append = next_image_pixels[0:offset]

                        if wall_thickness == 'solid' or wall_thickness > 1:
                            # if layer != len(img_list[image_number]) - 1:  # if not on the last layer
                            #     next_image_pixels = img_list[append_image_number][layer + 1]
                            #     img_pix_append = next_image_pixels[0:offset]  # first n pixels of next image
                            # else:
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
                        current_image_pixels = np.flip(current_image_pixels)  # flips orders of pixels because print direction is "negative"
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


                current_img = np.append(img_pix_current, img_pix_append)  # part of next image starts at end

                # toggle_ON_white = toggle_ON_list[0]
                # toggle_OFF_white = toggle_OFF_list[0]
                #
                # toggle_ON_black = toggle_ON_list[1]
                # toggle_OFF_black = toggle_OFF_list[1]






                ##### This section determines where to turn pixels on and off in the print
                for pix in range(len(current_img)):
                    pixel = current_img[pix]

                    # if pixel != white and pixel != black:
                    #     pixel = gray

                    if layer == 0 and first_toggle == True:
                        if pixel == white:
                            color_number = 0
                            # print(toggle_ON_white)
                            # black_ON_flag = False
                            # white_ON_flag = True
                        elif pixel == black:
                            color_number = 1
                            # print(toggle_ON_black)
                            # black_ON_flag = True
                            # white_ON_flag = False
                        else:
                            color_number = 2

                        print(toggle_ON_list[color_number])
                        ON_color = color_number
                        first_toggle = False

                    elif prev_pixel != pixel:
                        if pixel == white:
                            color_number = 0

                        elif pixel == black:
                            color_number = 1

                        else:
                            color_number = 2


                        if current_distance != 0:
                            if visualize_ON == ON_color:
                                print('G0 ' + str(variable) + str(sign * (current_distance * scale_factor)))
                            else:
                                print('G1 ' + str(variable) + str(sign * (current_distance * scale_factor)))


                        print(toggle_ON_list[color_number])
                        print(toggle_OFF_list[ON_color])
                        ON_color = color_number

                        current_distance = 0

                    current_distance += 1
                    prev_pixel = pixel

                    if pix == len(img_pix_current) - 1 and current_distance != 0:
                        if visualize_ON == ON_color:
                            print('G0 ' + str(variable) + str(sign * (current_distance*scale_factor)))
                        else:
                            print('G1 ' + str(variable) + str(sign * (current_distance * scale_factor)))


                        #prev_pixel = ''
                        current_distance = 0
                if current_distance != 0:
                    if visualize_ON == ON_color:
                        print('G0 ' + str(variable) + str(sign * (current_distance * scale_factor)))
                    else:
                        print('G1 ' + str(variable) + str(sign * (current_distance * scale_factor)))

        print('G1 ' + str(z_var) + str(z))

    # if black_ON_flag == True:
    #     print(toggle_OFF_black)
    # else:
    #     print(toggle_OFF_white)

    print(toggle_OFF_list[ON_color])

    return G_list, var_list, dist_list, command_list

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    image1 = 'img.png'#'checkerboard_invert_30x30pix.png'#'blue_jay_75x75pixs_3colors.png' #'Missouri.png'#'checkerboard_30x30pix.png'  # 'Heart50x50.png'#flask_30pix.png'  # 'temp_aaron.png'#'temp_heart.png'
    image2 = 'img.png'#'checkerboard_30x30pix.png'#'blue_jay_75x75pixs_3colors.png' #'VA_is4LOVERS.png'#'checkerboard_invert_30x30pix.png'  # 'checkerboard_invert_30x30pix.png' #'Heart50x50.png'#happy_chemistry_spill_30pix.png'  # 'temp_smiley.png'
    image3 = 'img.png'#'checkerboard_invert_30x30pix.png'#'blue_jay_75x75pixs_3colors.png' #'Missouri.png'#'checkerboard_30x30pix.png'  # 'Heart50x50.png'#'happy_chemistry_spill_30pix.png'  # 'temp_heart.png'
    image4 = 'img.png'#'checkerboard_30x30pix.png'#'blue_jay_75x75pixs_3colors.png' #'VA_is4LOVERS.png'#'checkerboard_invert_30x30pix.png'  # 'checkerboard_invert_30x30pix.png' #'Heart50x50.png' #'flask_30pix.png'  # 'temp_sarah_waz.png'


    ## To view in g-code simulator (https://nraynaud.github.io/webgcode/):
    visualize_ON = 1 # 0 = white, 1 = black, 2 = gray

    ## Geometry
    wall_thickness = 5 # 'solid'  # OPTIONS: a number or 'solid'
    fil_width = 1 # filament spacing
    z_height = 1  # layer height
    z_var = "Z"  # for use in aerotech

    ## Offset compensation
    offset = 0 # in mm - must be an integar multiple of the filament width

    pressure = [22, 22, 22]

    ######################################################################################################################
    com = ["serialPort1", "serialPort2", "serialPort3"]

    setpress1 = str('\n\r' + com[0] + '.write(' + str(setpress(pressure[0])) + ')')  # material 1
    setpress2 = str('\n\r' + com[1] + '.write(' + str(setpress(pressure[1])) + ')')  # material 2
    setpress3 = str('\n\r' + com[2] + '.write(' + str(setpress(pressure[2])) + ')')  # material 2


    white_ON = str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')')  # turn on material 1
    white_OFF = white_ON

    black_ON = str('\n\r' + com[1] + '.write(' + str(togglepress()) + ')')  # start 2nd material
    black_OFF = black_ON  # '\n'  # "\nM792 ;SEND Ultimus_IO["+str(comRight)+"]= 0" #stop 2nd material

    gray_ON = str('\n\r' + com[2] + '.write(' + str(togglepress()) + ')')  # start 3rd material
    gray_OFF = gray_ON

    ##################################################################################################
    toggle_ON_list = [
        white_ON,
        black_ON,
        gray_ON
    ]

    toggle_OFF_list = [
        white_OFF,
        black_OFF,
        gray_OFF
    ]

    image_list = [image1, image2, image3, image4]

    output = image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height,
                                     z_var, wall_thickness, offset)




































