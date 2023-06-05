import cv2
import numpy as np

'''NOTES
* all images must be the same size
* 1 pixel = 1 mm
* filament spacing and z height  = 1 mm (in current version)
'''
def image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, offset_ON, offset_OFF):
    black = 0
    white = 255
    img_list = []
    for image in image_list:
        img = cv2.imread(image, 0)
        img = cv2.flip(img, 0) # flip over y-axis
        img_list.append(img)  # converts images to pixels

    img_shape = img_list[0].shape # finds width and height of image (will use the first image in the last)
    height = img_shape[0]
    width = img_shape[1]

    num_layers = int(height)
    wall_thickness = int(width/2)

    North_ON = toggle_ON_list[0]
    South_ON = toggle_ON_list[1]
    East_ON = toggle_ON_list[2]
    West_ON = toggle_ON_list[3]

    North_OFF = toggle_OFF_list[0]
    South_OFF = toggle_OFF_list[1]
    East_OFF = toggle_OFF_list[2]
    West_OFF = toggle_OFF_list[3]

    ### This section creates the spiral print path
    current_length = fil_width
    p_list_A = []  # relative coordinate
    dir_list_A = []  # direction of nozzle
    face_list_A = []  # face on the cube

    for wall in range(wall_thickness):
        # N -> W -> S -> E (A layers go outward)
        p1 = [0, current_length]       # NORTH
        p2 = [-current_length, 0]      # WEST
        current_length += fil_width
        p3 = [0, -current_length]      # SOUTH
        p4 = [current_length, 0]       # EAST

        current_length += fil_width

        p_list_A.append(p1)
        dir_list_A.append('North')      # direction of nozzle
        face_list_A.append('East')      # face on the cube

        p_list_A.append(p2)
        dir_list_A.append('West')
        face_list_A.append('North')

        p_list_A.append(p3)
        dir_list_A.append('South')
        face_list_A.append('West')

        p_list_A.append(p4)
        dir_list_A.append('East')
        face_list_A.append('South')

        if (wall+1) == wall_thickness:
            current_length -= 1
            p_final = [0, current_length]
            p_list_A.append(p_final)
            dir_list_A.append('North')
            face_list_A.append('East')

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

    ## This section makes sure the final layer does not have dollop in the center
    if height%2 == 0: # if the height is an even number
        p_list_odd = p_list_A
        dir_list_odd = dir_list_A
        face_list_odd = face_list_A

        p_list_even = p_list_B
        dir_list_even = dir_list_B
        face_list_even = face_list_B

        outer_edge_list_odd = p_list_odd[-4:]
        outer_edge_list_even = p_list_even[0:4]
        reverse_pixels = 'even' # reverses pixels when layer is even

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


    # print(outer_edge_list_odd)
    # print(outer_edge_list_even)
    # print(reverse_pixels)

    #### This section creates the final print path that will be used
    z = z_height
    prev_pixel = ''
    prev_valve_OFF = ''
    print('G91')
    for layer in range(num_layers):
        print(';---LAYER-----', layer+1)
        if (layer + 1)%2 != 0:
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

        #print('---outer edge---', outer_edge_list)

        for coordinates in range(len(p_list)):
            if p_list[coordinates] not in outer_edge_list:
                print('G1 X' + str(p_list[coordinates][0]) + ' Y' + str(p_list[coordinates][1]))

            elif p_list[coordinates] in outer_edge_list:

                current_face = face_list[coordinates]
                current_dir = dir_list[coordinates]
                print(';---current face----', current_face)
                print(';---current dir----', current_dir)

                if current_dir == 'North':
                    valve_on = North_ON
                    valve_OFF = North_OFF
                    variable = 'Y'
                    sign = ''

                if current_dir == 'South':
                    valve_on = South_ON
                    valve_OFF = South_OFF
                    variable = 'Y'
                    sign = '-'

                if current_dir == 'East':
                    valve_on = East_ON
                    valve_OFF = East_OFF
                    variable = 'X'
                    sign = ''

                if current_dir == 'West':
                    valve_on = West_ON
                    valve_OFF = West_OFF
                    variable = 'X'
                    sign = '-'

                if current_face == 'East':  # Image 1, nozzle moving North or South
                    current_img = img_list[0][layer]

                if current_face == 'North':  # Image 2, nozzle moving East or West
                    current_img = img_list[1][layer]
                    current_img = current_img[1:]

                if current_face == 'West':  # Image 3, nozzle moving North or South
                    current_img = img_list[2][layer]

                if current_face == 'South':  # Image 4, nozzle moving East or West
                    current_img = img_list[3][layer]

                if layer_flag == reverse_pixels:
                    current_img = np.flip(current_img)

                current_distance = 0
                offset = 0
                for pixel in current_img:
                    if pixel != white:
                        pixel = black

                    if prev_pixel != pixel:
                        if pixel == black:
                            offset = offset_ON
                            print('G1 ' + str(variable) + str(sign) + str(current_distance - offset))
                            print(valve_on)
                        elif pixel != black and layer > 0:
                            offset = offset_OFF
                            if visualize_ON == True:
                                print('G0 ' + str(variable) + str(sign) + str(current_distance - offset))
                            else:
                                print('G1 ' + str(variable) + str(sign) + str(current_distance - offset))

                            print(prev_valve_OFF)
                        current_distance = offset

                    current_distance += 1
                    prev_pixel = pixel
                    prev_valve_OFF = valve_OFF


                print('G1 ' + str(variable) + str(sign) + str(current_distance))


        print('G1 '+str(z_var) + str(z))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    image1 = 'temp_aaron.png'#'temp_S_55.png' #'temp_aaron.png'#'temp_heart.png'
    image2 = 'temp_smiley.png'#'temp_heart_55.png' #'temp_smiley.png'
    image3 = 'temp_heart.png'#'temp_star_55.png' #'temp_heart.png'
    image4 = 'temp_sarah_waz.png'#'temp_smiley_55.png'#'temp_sarah_waz.png'

    visualize_ON = True
    offset_ON = 0
    offset_OFF = 0
    fil_width = 1
    z_height = 1
    z_var = "Z"

    North_ON = 'North ON'
    South_ON = 'South ON'
    West_ON = 'West ON'
    East_ON = 'East ON'

    North_OFF = 'North OFF'
    South_OFF = 'South OFF'
    West_OFF = 'West OFF'
    East_OFF = 'East OFF'


    toggle_ON_list = [North_ON, South_ON, East_ON, West_ON]
    toggle_OFF_list = [North_OFF, South_OFF, East_OFF, West_OFF]


    image_list = [image1, image2, image3, image4]
    image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, offset_ON, offset_OFF)


    # import turtle
    #
    # t = turtle.Turtle()
    # side = 0
    # for i in range(100):
    #    t.forward(side)
    #    t.right(90) #Exterior angle of a square is 90 degree
    #    side = side + 2

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

