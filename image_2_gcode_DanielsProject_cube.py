import cv2
import numpy as np

'''NOTES
* all images must be the same size
* 1 pixel = 1 mm
* smallest feature must be > offset
* distance to edge must > offset 
'''

def image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, inner_cube_width, offset_ON, offset_OFF):
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

    ### This section creates the spiral print path
    current_length = inner_cube_width
    if inner_cube_width == 0:
        current_length = fil_width

    p_list_A = []  # relative coordinate
    dir_list_A = []  # direction of nozzle
    face_list_A = []  # face on the cube

    #for wall in range(wall_thickness):
    while current_length <= width:
        # N -> W -> S -> E (A layers go outward)
        p1 = [0, current_length]       # NORTH
        p2 = [-current_length, 0]      # WEST

        p_list_A.append(p1)
        dir_list_A.append('North')  # direction of nozzle
        face_list_A.append('East')  # face on the cube

        p_list_A.append(p2)
        dir_list_A.append('West')
        face_list_A.append('North')

        if current_length >= width:
            p_final = [0, -current_length]
            p_list_A.append(p_final)
            dir_list_A.append('South')
            face_list_A.append('West')

            break

        current_length += fil_width
        p3 = [0, -current_length]      # SOUTH
        p4 = [current_length, 0]       # EAST

        p_list_A.append(p3)
        dir_list_A.append('South')
        face_list_A.append('West')

        p_list_A.append(p4)
        dir_list_A.append('East')
        face_list_A.append('South')

        if current_length >= width:
            #current_length -= 1
            p_final = [0, current_length]
            p_list_A.append(p_final)
            dir_list_A.append('North')
            face_list_A.append('East')

            break

        else:
            current_length += fil_width


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
                    if current_face == 'East':
                        valve_on = dirNorth_faceEast_ON
                        valve_OFF = dirNorth_faceEast_OFF
                    elif current_face == 'West':
                        valve_on = dirNorth_faceWest_ON
                        valve_OFF = dirNorth_faceWest_OFF

                    variable = 'Y'
                    sign = ''

                if current_dir == 'South':
                    if current_face == 'East':
                        valve_on = dirSouth_faceEast_ON
                        valve_OFF = dirSouth_faceEast_OFF
                    elif current_face == 'West':
                        valve_on = dirSouth_faceWest_ON
                        valve_OFF = dirSouth_faceWest_OFF

                    variable = 'Y'
                    sign = '-'

                if current_dir == 'East':
                    if current_face == 'North':
                        valve_on = dirEast_faceNorth_ON
                        valve_OFF = dirEast_faceNorth_OFF
                    elif current_face == 'South':
                        valve_on = dirEast_faceSouth_ON
                        valve_OFF = dirEast_faceSouth_OFF
                    variable = 'X'
                    sign = ''

                if current_dir == 'West':
                    if current_face == 'North':
                        valve_on = dirWest_faceNorth_ON
                        valve_OFF = dirWest_faceNorth_OFF
                    elif current_face == 'South':
                        valve_on = dirWest_faceSouth_ON
                        valve_OFF = dirWest_faceSouth_OFF

                    variable = 'X'
                    sign = '-'

                if current_face == 'East':  # Image 1, nozzle moving North or South
                    current_img = img_list[0][layer]

                if current_face == 'North':  # Image 2, nozzle moving East or West
                    current_img = img_list[1][layer]
                    #current_img = current_img[1:]

                if current_face == 'West':  # Image 3, nozzle moving North or South
                    current_img = img_list[2][layer]

                if current_face == 'South':  # Image 4, nozzle moving East or West
                    current_img = img_list[3][layer]

                if current_face == outer_face_short:   # edge of img (first pixel) is replaced by +Z movement
                    current_img = current_img[1:]

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
    image1 = 'temp_S_55.png' #'temp_aaron.png'#'temp_heart.png'
    image2 = 'temp_heart_55.png' #'temp_smiley.png'
    image3 = 'temp_star_55.png' #'temp_heart.png'
    image4 = 'temp_smiley_55_v2.png'#'temp_sarah_waz.png'

    ## To view in g-code simulator (https://nraynaud.github.io/webgcode/):
    visualize_ON = True

    ## Geometry
    inner_cube_width = 30    # removes center of cube if > 0
    fil_width = 1           # filament spacing
    z_height = 1            # layer height
    z_var = "D"             # for use in aerotech

    ## Offset compensation
    offset_ON = 0
    offset_OFF = 0

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

    image2gcode_spiral_cube(image_list, toggle_ON_list, toggle_OFF_list, visualize_ON, fil_width, z_height, z_var, inner_cube_width, offset_ON, offset_OFF)
