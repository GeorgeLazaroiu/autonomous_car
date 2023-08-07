# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 20:07:58 2023

@author: George LAZAROIU
"""

import argparse
import textwrap

class ArgumentParser(object):
    
    def __init__(self):
        self.__parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                                    SELF DRIVING CAR 
                                    LAZAROIU GEORGE
        -----------------------------------------------------------------------
            This project implements an autonomous car, using raspberry pi,
            capable of driving withing the lane lines and detecting traffic 
            signs such as stop, red/green light and speed limit
        '''), 
            formatter_class=argparse.RawTextHelpFormatter)
        
        self.__append_args()
        
        
    def __append_args(self):
        if self.__parser is None:
            return
        
        self.__parser.add_argument('--debug', action='store_true', help='display debug messages')
        self.__parser.add_argument('--feed', choices={0,1,2,3,4}, default=0, 
                                   help='display live feed from the camera\n' 
                                        ' 0 - display all available feeds\n'
                                        ' 1 - display only the final feed\n'
                                        ' 2 - dont display any feed\n'
                                        ' 3 - display all line detection related feeds\n'
                                        ' 4 - display all object recognition related feeds\n',
                                   type=int)
        self.__parser.add_argument('--fps', action='store_true', help='display the fps on each feed')
        self.__parser.add_argument('--speed', choices={0, 20, 25, 30}, default=20, help='the default speed of the car\n'
                                                                                       'any change in the speed of the car will\n'
                                                                                       'be proportional to the default speed',
                                   type=int)
        self.__parser.add_argument('--mode', choices={0, 1, 2}, default=0, help='the drive mode of the car\n' 
                                                                                ' 0 - all systems on\n'
                                                                                ' 1 - only lane detection\n'
                                                                                ' 2 - only object recognition\n',
                                    type=int)
        
    def parse(self):
        if self.__parser is None:
            return None
        
        args, unknown = self.__parser.parse_known_args()
        return args
        
