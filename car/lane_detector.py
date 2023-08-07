# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 19:11:40 2023

@author: George LAZAROIU
"""

import cv2
import math
import numpy as np

import utils.geometry as geometry
import constants.constants as constants
from utils.logger import Logger, LogSeverity
from utils.camera import CameraFeed, FrameType

class LaneDetector(object):
    
    def __init__(self, feed: CameraFeed, logger: Logger):
        self.__feed = feed
        self.__logger = logger
        
    def get_steering_angle(self, frame, current_steering_angle):
        lane_lines, frame = self.__detect_lane_lines(frame)
        
        if len(lane_lines) < 1 or len(lane_lines) > 2:
            self.__logger.log('Invalid number of lines detected ...', LogSeverity.ERROR)
            return current_steering_angle
        
        lane_lines_frame = self.__display_lane_lines(frame, lane_lines)
        self.__feed.display_frame("Detected Lane Lines", lane_lines_frame, FrameType.LINE_DETECTION)
        
        steering_angle = self.__compute_steering_angle(frame, lane_lines)
        if steering_angle == -1:
            return current_steering_angle
        
        final_steering_angle = self.__stabilize_steering_angle(current_steering_angle, steering_angle, len(lane_lines))
        heading_line_frame = self.__display_median_line(frame, final_steering_angle)
        self.__feed.display_frame("Heading Line", heading_line_frame, FrameType.LINE_DETECTION)
        
        return final_steering_angle
        
    def __stabilize_steering_angle(self, curr_steering_angle, new_steering_angle, num_of_lane_lines):
        if num_of_lane_lines == 2 :
            max_angle_deviation = constants.MAX_ANGLE_DEVIATION_FOR_2_LINES
        else :
            max_angle_deviation = constants.MAX_ANGLE_DEVIATION_FOR_1_LINES
        
        angle_deviation = new_steering_angle - curr_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(curr_steering_angle
                                            + max_angle_deviation * angle_deviation / abs(angle_deviation))
                                            
        else:
            stabilized_steering_angle = new_steering_angle

        return stabilized_steering_angle
        
    def __compute_steering_angle(self, frame, lane_lines):
        x_offset, y_offset = geometry.detect_far_median_point(frame, lane_lines)
        
        if y_offset == 0:
            self.__logger.log('Invalid median point ...', LogSeverity.ERROR)
            return -1
        
        angle_to_mid_radian = math.atan(x_offset / y_offset)  
        
        return geometry.from_rad_to_deq(angle_to_mid_radian) + 90
        
    def __detect_lane_lines(self, frame):
        edges = self.__detect_edges(frame)
        
        self.__feed.display_frame("Edge Detection", edges, FrameType.LINE_DETECTION)
        
        region_of_interest = self.__extract_region_of_interest(edges)
        
        self.__feed.display_frame("Region of interest", region_of_interest, FrameType.LINE_DETECTION)
        
        segments = self.__detect_segments(region_of_interest)
        
        return geometry.detect_lane_lines(frame, segments), frame
        
    def __detect_edges(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        self.__feed.display_frame("HSV", hsv, FrameType.LINE_DETECTION)
        
        lower_blue = np.array(constants.BLUE_DETECTION_THRESHOLD_LOWER_BOUND)
        upper_blue = np.array(constants.BLUE_DETECTION_THRESHOLD_UPPER_BOUND)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        self.__feed.display_frame("Blue Detection", mask, FrameType.LINE_DETECTION)
        
        edges = cv2.Canny(mask, 200, 400)

        return edges
    
    def __extract_region_of_interest(self, edges):
        height, width = edges.shape
        mask = np.zeros_like(edges)

        polygon = np.array([[
            (0, height * constants.REGION_OF_INTEREST_RATIO),
            (width, height * constants.REGION_OF_INTEREST_RATIO),
            (width, height),
            (0, height),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        region_of_interest = cv2.bitwise_and(edges, mask)
        return region_of_interest
    
    def __detect_segments(self, region_of_interest):
        rho = 1
        angle = np.pi / 180
        min_threshold = constants.SEGMENT_DETECTION_VOTES_THRESHOLD
        line_segments = cv2.HoughLinesP(region_of_interest, rho, angle, 
                                        min_threshold, np.array([]), 
                                        minLineLength=constants.MIN_LINE_DETECTION_LENGTH, 
                                        maxLineGap=constants.MAX_LINE_DETECTION_GAP)

        return line_segments
    
    def __display_lane_lines(self, frame, lines):
        line_image = np.zeros_like(frame)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), constants.LANE_COLOR, constants.LANE_WIDTH)
        line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
        return line_image
    
    def __display_median_line(self, frame, steering_angle):
        heading_image = np.zeros_like(frame)
        height, width, _ = frame.shape
        
        steering_angle_radian = steering_angle / 180.0 * math.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
        y2 = int(height / 2)

        cv2.line(heading_image, (x1, y1), (x2, y2), constants.HEADING_LINE_COLOR, constants.HEADING_LINE_WIDTH)
        heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

        return heading_image
    
    
