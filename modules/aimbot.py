"""Aimbot 
* Makes screenshot from window, moves mouse and shoots.

author: inf20079@lehre.dhbw-stuttgart.de
dat: 03.05.2022
version: 0.0.1
license: MIT

"""

import logging
from datetime import datetime
import pywin32_system32

class Aimbot():

    def __init__(self, windowname:str=None, logger:logging.Logger=None) -> None:
        if windowname is None:
            self.windowname = "Doomstein98 - Google Chrome"

        if logger is None:
            # Logging level
            if self.debug:
                logging_level = logging.DEBUG
            else:
                logging_level = logging.INFO

            # Get logger
            self.logger = logging.getLogger(name="Object detection")
            # Set level
            self.logger.setLevel(logging_level)
            # create formatter
            formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
            # logging file name
            name = f'./log/object_detection{datetime.now()}.log'
            # Logging file handler
            file_handler = logging.FileHandler(name)
            file_handler.setFormatter(formatter)
            # Add components
            self.logger.addHandler(file_handler)
        else: 
            self.logger = logger

    def getWindowPosition(self, windowname:str):
        """Gets the position of the desired window.

        Args:
            windowname (str): Defines the window to get the position of.
        
        Returns:
            region (Array): Contains edges of the window

        Test:

        """
        # Search fro window and get rect
        hwnd = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive')
        #hwnd = win32gui.FindWindow("UnrealWindow", None) # Fortnite
        rect = win32gui.GetWindowRect(hwnd)
        region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

    def getScreenshotOfWindow(self, region):
        """Screenshots the game

        Args:
            region (_type_): Pixel region where the game is on the desktop.

        Returns:
            numpyimage (image): Screenshotted image of the game.
        """


        pass

    def calculatePositionOfClosestPlayer(self, detections, fovoffset:float=0):
        """Calculate which bounding box is closest to the crosshair.

        Args:
            detections (array): Bounding boxes of detected players.
            fovoffset (optional, float): The discreptancy of the xy-position of the player and the actual position of the pixel. Defaults to 0.

        Returns:
            x (int): X-pixel of the players position
            y (int): Y-pixel of the players position
        """

        """ TODO: 
            - Calculate position of the player
        """
        pass

    def moveMouseAndShoot(self, x:int, y:int):
        """Moves the mouse to the player and shoots

        Args:
            x (int): X-position of the player.
            y (int): Y-position of the player.
        """
        pass
