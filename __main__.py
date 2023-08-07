# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 20:08:19 2023

@author: George LAZAROIU
"""
from utils.logger import Logger
from car.car import AutonomousCar
from utils.camera import CameraFeed
from utils.cli import ArgumentParser

parser = ArgumentParser()
args = parser.parse()

logger = Logger(args.debug)

feed = CameraFeed(logger, args.fps, args.feed)

print(args.mode)
car = AutonomousCar(logger, feed, args.speed, args.mode)
try:
	car.drive()
except KeyboardInterrupt:
	car.cleanup()


