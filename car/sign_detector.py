# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 19:12:13 2023

@author: George LAZAROIU
"""
import cv2

from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

import constants.constants as constants
from utils.logger import Logger, LogSeverity
from utils.camera import CameraFeed, FrameType

class SignDetector(object):
    
    def __init__(self, feed: CameraFeed, logger: Logger):
        self.__feed = feed
        self.__logger = logger
        
        self.__initialize_model()
        self.__initialize_labels()
        
        self.__speed_ratios = {constants.GREEN_LIGHT: constants.DEFAULT_SPEED_RATIO,
                               constants.SPEED_60:   constants.SPEED_RATIO_60,
                               constants.RED_LIGHT:   constants.STOP_SPEED_RATIO,
                               constants.SPEED_20:   constants.SPEED_RATIO_40,
                               constants.SPEED_40:   constants.SPEED_RATIO_40,
                               constants.STOP:       constants.STOP_SPEED_RATIO}
    
    def get_detected_sign_and_speed(self, frame):
       detected_objects = self.__detect_objects(frame)
       self.__draw_detected_objects(frame, detected_objects)
       return self.__detect_new_speed(detected_objects)
       
    def __initialize_labels(self):
        self.__logger.log('Initializing model labels ...', LogSeverity.INFO)
        
        with open(constants.LABELS_PATH, 'r') as file:
            pairs = (l.strip().split(maxsplit=1) for l in file.readlines())
            self.__labels = dict((int(k), v) for k, v in pairs)
            
    def __initialize_model(self):
        self.__logger.log('Initializing model model ...', LogSeverity.INFO)
        
        base_options = core.BaseOptions(file_name=constants.MODEL_PATH, use_coral=False, num_threads=4)
        detection_options = processor.DetectionOptions(max_results=3, score_threshold=0.3)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        self.__engine = vision.ObjectDetector.create_from_options(options)
        
    def __detect_objects(self, frame):
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = vision.TensorImage.create_from_array(frame_RGB)
        
        detected_objects = self.__engine.detect(img_pil)
        
        if not detected_objects.detections:
            self.__logger.log('No objects detected ...', LogSeverity.WARNING)
        
        return detected_objects.detections
    
    def __draw_detected_objects(self, frame, detected_objects):
        for obj in detected_objects:
            box = obj.bounding_box
            coord_top_left = box.origin_x, box.origin_y
            coord_bottom_right = box.origin_x + box.width, box.origin_y + box.height
            
            category = obj.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            
            cv2.rectangle(frame, coord_top_left, coord_bottom_right, constants.BOX_COLOR, constants.BOX_LINE_WIDTH)
            
            annotate_text = "%s %.0f%%" % (category_name, probability * 100)
            coord_top_left = (coord_top_left[0], coord_top_left[1] + 15)
            cv2.putText(frame, annotate_text, coord_top_left, cv2.FONT_HERSHEY_SIMPLEX, constants.FONT_SCALE, constants.BOX_COLOR, constants.BOX_LINE_WIDTH)
        
        self.__feed.display_frame("Detected objects", frame, FrameType.OBJECT_DETECTION)
        
    def __detect_new_speed(self, detected_objects):
        print(detected_objects)
        for obj in detected_objects:
            if self.__is_object_close(obj):
                obj_label = obj.categories[0].category_name
                log = "Detected {detected_sign} ..."
                self.__logger.log(log.format(detected_sign = obj_label), LogSeverity.INFO)
                return self.__speed_ratios[obj_label], obj_label
            
    def __is_object_close(self, detected_object):
        obj_height = detected_object.bounding_box.height
        return obj_height / constants.CAMERA_FRAME_HEIGHT > constants.CLOSE_OBJECT_TRESHOLD
