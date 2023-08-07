# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 19:59:17 2023

@author: George LAZAROIU
"""
import math
import numpy as np
import constants.constants as constants

def detect_lane_lines(frame, line_segments):
    lane_lines = []
    if line_segments is None:
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/2
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(get_line_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(get_line_points(frame, right_fit_average))

    return lane_lines

def detect_far_median_point(frame, lane_lines):
    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        x1, y1, x2, y2 = lane_lines[0][0]
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        left_x1, left_y1, left_x2, left_y2 = lane_lines[0][0]
        right_x1, right_y1, right_x2, right_y2 = lane_lines[1][0]
        
        camera_mid_offset_percent = 0.045 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # HEIGHT / CAT AI TAIAT DIN IMAGINE CA SA OBTII REGIUNEA DE INTERES GEN
    y_offset = int(height / 2)
    
    return x_offset, y_offset

def get_line_length(line):
    x1, y1, x2, y2 = line
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_line_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def from_rad_to_deq(rad):
    return int(rad * 180.0 / math.pi)
