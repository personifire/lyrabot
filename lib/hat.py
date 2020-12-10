import math
import os
import random

import cv2
import numpy as np
import requests

HATDIR = 'files/santahats'
OUTDIR = 'data'

def get_hats():
    return [f'{HATDIR}/{hat_name}' for hat_name in os.listdir(HATDIR)]

def line_detect(img):
    edges = cv2.Canny(img, 100, 200) # very arbitrary threshold values

    if edges is None:
        return None # likely a .gif or other unsupported format -- TODO figure out how to support (low priority)

    rho = 1                # distance resolution (how far apart two points can be before getting lumped together)
    theta = 5 * 3.14 / 180 # angle resolution (how different slopes can be before getting lumped together)
    threshold = 2          # accumulator threshold parameter, minimum "votes" to be a line
    minLineLength = 0.5    # minimum length for a line to "count"
    maxLineGap = 1         # maximum distance between points on the same line allowed before "linking"
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength = minLineLength, maxLineGap = maxLineGap) # lines is [(x1, y1, x2, y2), p2, etc.]

    return lines


def dict_index_insert(dictionary, index, value):
    if index in dictionary:
        dictionary[index].append(value)
    else:
        dictionary[index] = [value]

def index_lines(lines, min_x, max_x):
    # organize lines: hash line_dict { pt1 => [pt2, ...], pt2 => [pt1, ...] }
    line_dict = {}
    # index center pts: hash y_idx_pts { y1 => [x1, ...], y2 => [x2, ...] }
    y_idx_pts = {}
    for line in lines:
        line = line[0]
        p1 = (line[0], line[1])
        p2 = (line[2], line[3])

        #if p1 == p2: # remove zero-length lines
        #    continue

        # only track x in the center third
        if min_x <= p1[0] and p1[0] <= max_x:
            dict_index_insert(y_idx_pts, p1[1], p1[0])
        if min_x <= p2[0] and p2[0] <= max_x:
            dict_index_insert(y_idx_pts, p2[1], p2[0])

        dict_index_insert(line_dict, p1, p2)
        dict_index_insert(line_dict, p2, p1)
    return line_dict, y_idx_pts

def slope(p1, p2):
    dx = p1[0] - p2[0]
    if dx == 0:
        return 999 # might as well be infinity tbqh
    else:
        return (p1[1] - p2[1]) / dx

def neighborhood(point):
    """ return a small neighborhood around a given point
    the points in this neighborhood are mildly arbitrary, but have given good results so far
    """
    p_x = point[0]
    p_y = point[1]
    points  = [(x, y) for x in range(p_x - 1, p_x + 2) for y in range(p_y - 1, p_y + 2)]
    points += [(p_x - 2, p_y), (p_x + 2, p_y)]
    return points

def expand_line(x_val, y_val, lines, expand_left = True):
    """ given a point, join together lines going left (or right) as far as possible
    stop when the slope is outside the range [-1.5, 1.5]
    """
    max_slope_magnitude = 1.5

    frontier = set(neighborhood((x_val, y_val)))
    visited = frontier

    # do a BFS deal
    extreme = (x_val, y_val)
    if expand_left:
        is_addable = lambda point, origin: point not in visited and abs(slope(point, origin)) <= max_slope_magnitude and point[0] <= origin[0]
    else:
        is_addable = lambda point, origin: point not in visited and abs(slope(point, origin)) <= max_slope_magnitude and point[0] >= origin[0]
    while len(frontier) > 0:
        next_frontier = set()
        for origin in frontier:
            points = lines.get(origin)
            if points is None:
                continue
            for endpoint in points:
                for point in neighborhood(endpoint):
                    if is_addable(point, origin):
                        next_frontier.update(set(neighborhood(point)))
        frontier = next_frontier
        visited |= frontier

    # choose the most leftward/rightward point
    extreme = (x_val, y_val)
    for point in visited:
        if expand_left and point[0] < extreme[0]:
            extreme = point
        elif not expand_left and point[0] > extreme[0]:
            extreme = point

    return extreme

def norm_squared(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return (dx * dx) + (dy * dy)

def pick_points(y_idx_pts, line_dict, height_target, min_length, max_attempts = 5):
    """ do arbitrary bs to find a line that might be good to place a hat on """
    # find points around the height_target
    y_values = sorted(y_idx_pts.keys())
    nice_low, nice_high = 0, len(y_values)
    while nice_low < nice_high:
        mid = (nice_low + nice_high) // 2
        if y_values[mid] < height_target:
            nice_low = mid + 1
        else:
            nice_high = mid - 1
    nice_idx = nice_high

    hat_lines = []
    hat_good = False
    for attempt in range(max_attempts):
        # somehow choose a good point/line (this is totally arbitrary bs)
        if nice_idx >= len(y_values):
            nice_idx = len(y_values) - 1
        nice_y = y_values[nice_idx]
        del y_values[nice_idx] # visit each y value only once (also arbitrary bs)

        x_vals = y_idx_pts[nice_y]
        nice_x = x_vals[len(x_vals) // 2]

        # expand the line and see where it takes us
        hat_p1 = expand_line(nice_x, nice_y, line_dict, True)
        hat_p2 = expand_line(nice_x, nice_y, line_dict, False)

        hat_lines.append((hat_p1, hat_p2))

    hat_p1, hat_p2 = max(hat_lines, key = lambda l: norm_squared(*l))

    return hat_p1, hat_p2

def transform_hat(hat, hat_p1, hat_p2, img_width, img_height, hat_width, hat_height):
    hat_length = math.hypot(hat_p1[1] - hat_p2[1], hat_p1[0] - hat_p2[0])
    hat_center = (hat_width // 2, hat_height // 2)

    angle = -math.degrees(math.atan2(hat_p2[1] - hat_p1[1], hat_p2[0] - hat_p1[0]))
    scale = hat_length / (hat_width // 2) # standard hat form takes up the center half of the image
    rot_matrix = cv2.getRotationMatrix2D(hat_center, angle, scale)
    rotated_hat = cv2.warpAffine(hat, rot_matrix, (hat_width, hat_height), flags=cv2.INTER_CUBIC)

    # crop hat so it fits inside the image when overlayed in the right position
    center_position = ((hat_p1[0] + hat_p2[0]) // 2, (hat_p1[1] + hat_p2[1]) // 2)

    space_above = center_position[1]
    space_left  = center_position[0]

    crop_above  = max(hat_center[1] - space_above, 0)
    crop_height = min(hat_height - crop_above, img_height - space_above + hat_center[1], img_height)
    crop_left   = max(hat_center[0] - space_left,  0)
    crop_width  = min(hat_width  - crop_left,  img_width  - space_left  + hat_center[0], img_width)

    cropped_hat = rotated_hat[crop_above:crop_above + crop_height, crop_left:crop_left + crop_width]

    # don't bother trying to add a transparent border, it is evidently not really feasible

    return cropped_hat

def hatten(img, hat, outname):
    # do some image processing
    lines = line_detect(img)
    if lines is None:
        return f"probably gif -- img {img} from {img_name} hat {hat_name} out {out_name}"

    img_height, img_width, img_num_channels = img.shape
    hat_height, hat_width, hat_num_channels = hat.shape

    # this resizing may not be a fantastic idea for processing time...
    if hat_width < img_width:
        hat = cv2.resize(hat, (img_width, img_width), cv2.INTER_CUBIC)
        hat_height, hat_width, hat_num_channels = hat.shape

    # reorganize some numbers
    third_width = img_width // 3
    line_dict, y_idx_pts = index_lines(lines, third_width, third_width * 2)

    # pick a line to enhat
    height_target = int(img_height * 0.2)
    min_length = img_width / 10 # this is a very smol minimum sized hat
    values = pick_points(y_idx_pts, line_dict, height_target, min_length)
    hat_p1, hat_p2 = values

    hat_length = math.hypot(hat_p1[1] - hat_p2[1], hat_p1[0] - hat_p2[0])
    hat_good = hat_length >= min_length
    if not hat_good:
        hat_p1 = (img_width // 3, img_height // 5)
        hat_p2 = (img_width * 4 // 5, img_height // 3)
        hat_length = math.hypot(hat_p1[1] - hat_p2[1], hat_p1[0] - hat_p2[0])

    # use endpoints to scale/rotate hat
    output_hat = transform_hat(hat, hat_p1, hat_p2, img_width, img_height, hat_width, hat_height)

    ohat_h, ohat_w, ohat_no_ch = output_hat.shape

    # then overlay hat and output
    hat_center = (hat_width // 2, hat_height // 2)
    hat_position = ((hat_p1[0] + hat_p2[0]) // 2, (hat_p1[1] + hat_p2[1]) // 2)

    i_y1 = max(hat_position[1] - hat_center[1], 0)
    i_y2 = i_y1 + ohat_h
    i_x1 = max(hat_position[0] - hat_center[0], 0)
    i_x2 = i_x1 + ohat_w

    debug_str  = "all the information is here:\n"
    debug_str += f"img_w {img_width} img_h {img_height}\n"
    debug_str += f"ohat_w {ohat_w} ohat_h {ohat_h}\n"
    debug_str += f"hat center point ({hat_position[0]}, {hat_position[1]})\n"
    debug_str += f"i_y {i_y1}:{i_y2}\n"
    debug_str += f"i_x {i_x1}:{i_x2}\n"
    print(debug_str)


    hat_alpha = output_hat[:, :, 3] / 255
    inv_hat_a = 1 - hat_alpha

    for c in range(3):
        img[i_y1:i_y2, i_x1:i_x2, c] = ((hat_alpha * output_hat[:, :, c]) +
                (inv_hat_a * img[i_y1:i_y2, i_x1:i_x2, c]))

    if img_num_channels > 3:
        inv_img_a = 1 - (img[i_y1:i_y2, i_x1:i_x2, 3] / 255)
        img[i_y1:i_y2, i_x1:i_x2, 3] = 255 * (1 - (inv_hat_a * inv_img_a))

    cv2.imwrite(outname, img)

    return hat_good


def enhat_image(imgname, outname, hatname = None, img_is_url = True):
    if hatname is None:
        hatname = random.choice(get_hats())
    else:
        hatname = f'{HATDIR}/{hatname}.png'

    if img_is_url:
        img_bytearray = np.asarray(bytearray(requests.get(imgname).content))#, dtype='uint8'))
        img = cv2.imdecode(img_bytearray, cv2.IMREAD_UNCHANGED)
    else:
        img = cv2.imread(img_name, flags=cv2.IMREAD_UNCHANGED)

    hat = cv2.imread(hatname, flags=cv2.IMREAD_UNCHANGED)

    return hatten(img, hat, outname)
