# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 18:15:28 2023

@author: George LAZAROIU
"""

import cv2
import time
from .controller import Controller
from .lane_detector import LaneDetector
from .sign_detector import SignDetector

import constants.constants as constants
from utils.logger import Logger, LogSeverity
from utils.camera import CameraFeed, FrameType

class AutonomousCar(object):
    
    def __init__(self, logger: Logger, feed: CameraFeed, default_speed: int, mode: int):
        self.__logger = logger
        self.__feed = feed
        self.__default_speed = default_speed
        self.__mode = mode
        self.__stop_detected = False
                
        self.__logger.log('Setting up car systems ...', LogSeverity.INFO)
        
        self.__controller = Controller(logger, default_speed)
        self.__lane_detector = LaneDetector(self.__feed, self.__logger)
        self.__sign_detector = SignDetector(self.__feed, self.__logger)
        
        self.__logger.log('Finished setting up car systems ...', LogSeverity.INFO)

        
    def cleanup(self):
        self.__controller.cleanup()
        
        
    def drive(self):
        self.__controller.update_speed(constants.DEFAULT_SPEED_RATIO)
        
        while self.__feed.recording():
            frame = self.__feed.get_frame()
            
            self.__feed.display_frame("Original", frame, FrameType.INITIAL)
            
            self.__follow_lane(frame)
            
            self.__detect_signs(frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.__controller.cleanup()
                break
                
    def __follow_lane(self, frame):
        if self.__mode == constants.ONLY_OBJECT_RECOGNITION:
            return
        
        steering_angle = self.__lane_detector.get_steering_angle(frame, 
            self.__controller.get_current_steering_angle())
        self.__controller.update_steering_angle(steering_angle)
        
    def __detect_signs(self, frame):
        if self.__mode == constants.ONLY_LANE_DETECTION:
            return
        
        current_speed = self.__controller.get_current_speed()
        new_speed = current_speed
        try:
            new_speed, detected_sign = self.__sign_detector.get_detected_sign_and_speed(frame)        
        except TypeError:
            return
        
        if detected_sign == constants.STOP:
            if self.__stop_detected == False:
                self.__stop_detected = True
                self.__controller.update_speed(new_speed)
                time.sleep(5)
                self.__controller.update_speed(current_speed/self.__default_speed)
        else:
            self.__controller.update_speed(new_speed)
            self.__stop_detected = False
