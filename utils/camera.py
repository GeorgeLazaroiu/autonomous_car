# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 14:02:03 2023

@author: George LAZAROIU
"""

import cv2
import enum
import time

from .logger import Logger, LogSeverity
import constants.constants as constants

class FrameType(enum.Enum):
    INITIAL = 0
    LINE_DETECTION = 1
    OBJECT_DETECTION = 2
    FINAL = 3 

class CameraFeed(object):
    
    def __init__(self, logger: Logger, fps: bool, feed_option: int):
        self.__logger = logger
        self.__fps = fps
        self.__feed_option = feed_option

        self.__new_timeframe = 0
        self.__pre_timeframe = 0
        self.__last_fps = 0
        
        self.__camera_setup()
        
    def __camera_setup(self):
        self.__logger.log('Setting up the camera ...', LogSeverity.INFO)
        
        self.__camera = cv2.VideoCapture(-1)
        self.__camera.set(3, constants.CAMERA_FRAME_WIDTH)
        self.__camera.set(4, constants.CAMERA_FRAME_HEIGHT)
        self.__camera.set(cv2.CAP_PROP_FPS, 60)
        
        self.__logger.log('Finished Setting up the camera ...', LogSeverity.INFO)
        
    def __show_frame(self, title, frame):
        cv2.imshow(title, self.__append_fps(frame))
        
    def __append_fps(self, frame):
        if self.__fps is False:
            return frame
        
        self.__new_timeframe = time.time()
        
        fps = 1 / (self.__new_timeframe - self.__pre_timeframe)
        self.__pre_timeframe = self.__new_timeframe
        fps = int(fps)
        self.__last_fps = fps
        cv2.putText(frame, str(fps), (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 4)
        return frame
    
    def recording(self):
        return self.__camera.isOpened()
    
    def get_frame(self):
        _, frame = self.__camera.read()
        return frame
    
    def display_frame(self, title, frame, frame_type: FrameType):
        if self.__feed_option == constants.DONT_DISPLAY_FEED:
            return
        elif self.__feed_option == constants.DISPLAY_ALL_FEED:
            self.__show_frame(title, frame)
        elif self.__feed_option == constants.DISPLAY_FINAL_FEED:
            if frame_type != FrameType.FINAL:
                if frame_type != FrameType.INITIAL:
                    return
        elif self.__feed_option == constants.DISPLAY_ALL_LINE_DETECTION_FEED:
            if frame_type != FrameType.LINE_DETECTION:
                if frame_type != FrameType.INITIAL:
                    return
        elif self.__feed_option == constants.DISPLAY_ALL_OBJECT_DETECTION_FEED:
            if frame_type != FrameType.OBJECT_DETECTION:
                if frame_type != FrameType.INITIAL:
                    return
        else:
            return
            
