# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 18:31:25 2023

@author: LAZAROIU GEORGE
"""
import picar

import constants.constants as constants
from utils.logger import Logger, LogSeverity


class Controller(object):

    def __init__(self, logger: Logger, default_speed: int):
        self.__logger = logger
        self.__default_speed = default_speed
        
        picar.setup()

        self.__current_steering_angle = constants.INITIAL_STEERING_ANGLE
        self.__current_speed = 0

        self.__logger.log('Setting up car controller ...', LogSeverity.INFO)


        """ Calibrating back wheels """
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0

        """ Calibrating front wheels """
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = 0
        self.front_wheels.turn(constants.INITIAL_STEERING_ANGLE)

        self.__logger.log('Finished setting up car controller ...', LogSeverity.INFO)

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, _type, value, traceback):
        """ Exit a with statement"""
        self.cleanup()

    def cleanup(self):
        """ Reset the hardware"""
        self.back_wheels.speed = 0
        self.front_wheels.turn(90)
        self.camera.release()
        cv2.destroyAllWindows()        


    def update_speed(self, ratio: float):
        """ Speed Range is 0 (stop) - 100 (fastest) """

        speed = min(self.__default_speed * ratio, constants.MAX_SPEED)
        
        self.back_wheels.speed = int(speed)
        self.__current_speed = speed

        log = "Changing speed to {new_speed:.2f} ..."
        self.__logger.log(log.format(new_speed=speed), LogSeverity.INFO)


    def update_steering_angle(self, angle: float):
        """ Steering Range is 45 (left) - 90 (center) - 135 (right) """

        if angle < constants.MIN_STEERING_ANGLE:
            angle = constants.MIN_STEERING_ANGLE

        if angle > constants.MAX_STEERING_ANGLE:
            angle = constants.MAX_STEERING_ANGLE

        self.front_wheels.turn(angle)
        self.__current_steering_angle = angle

        log = "Changing steering angle to {new_angle:.2f} ..."
        self.__logger.log(log.format(new_angle=angle), LogSeverity.INFO)


    def get_current_steering_angle(self):
        return self.__current_steering_angle


    def get_current_speed(self):
        return self.__current_speed
