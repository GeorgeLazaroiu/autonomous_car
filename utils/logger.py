# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 23:56:49 2023

@author: George LAZAROIU
"""

import enum
import logging

class LogSeverity(enum.Enum):
    INFO = 0
    ERROR = 1
    WARNING = 2

class Logger(object):
    
    def __init__(self, debug=True):
        self.__debug = debug
        
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-5s:%(asctime)s: %(message)s')
        
    def log(self, message: str, severity: LogSeverity):
        if not self.__debug:
            return
        
        if severity == LogSeverity.INFO:
            logging.debug(message)
        elif severity == LogSeverity.ERROR:
            logging.error(message)
        elif severity == LogSeverity.WARNING:
            logging.warning(message)
        
