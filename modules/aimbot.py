"""Aimbot
* Makes screenshot from window, moves mouse and shoots.

author: inf20079@lehre.dhbw-stuttgart.de
dat: 03.05.2022
version: 0.0.1
license: MIT

"""

import logging
from datetime import datetime
import math
import win32gui, win32api, win32con
from time import sleep
from modules.object_detector_darknet import ObjectDetector
import numpy as np
import pyautogui
import cv2

class Aimbot():
    """ Detects players in selected game window and shoots them.
    """
    def __init__(self, objectdetector:ObjectDetector=None, debug=False, windowname:str=None, fovoffsetx:float=1, fovoffsety:float=1, logger:logging.Logger=None) -> None:
        """ Creates a aimbot.

        Args:
            objectdetector (ObjectDetector, optional): Detects players. Defaults to None.
            windowname (str, optional): Name of the game window. Defaults to None.
            fovoffsetx (float, optional): Pixel offset in x-direction. Defaults to 1.
            fovoffsety (float, optional): Pixel offset in y-direction. Defaults to 1.
            logger (logging.Logger, optional): Logger. Either add one or the class will create one. Defaults to None.

        Tests:
            check if class can be instancianted with different sets of parameters.
        """
        # Create variables
        if windowname is None:
            self.windowname = "Doomstein98 - Google Chrome"
        else:
            self.windowname = windowname
        
        self.fovoffsetx = fovoffsetx
        self.fovoffsety = fovoffsety
        self.debug = debug

        # Create logger
        if logger is None:
            # Logging level
            if self.debug:
                logging_level = logging.DEBUG
            else:
                logging_level = logging.INFO

            # Get logger
            self.logger = logging.getLogger(name="Aimbot")
            # Set level
            self.logger.setLevel(logging_level)
            # create formatter
            formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
            # logging file name
            name = f'./log/aimbot.log'
            # Logging file handler
            file_handler = logging.FileHandler(name)
            file_handler.setFormatter(formatter)
            # Add components
            self.logger.addHandler(file_handler)
        else: 
            self.logger = logger

        # Add object detector
        if objectdetector is None:
            self.objectdetector = ObjectDetector(logger=self.logger, debug=self.debug)
        else:
            self.objectdetector = objectdetector

    def getWindowPosition(self, windowname:str="Doomstein98 - Google Chrome"):
        """Gets the position of the desired window.

        Args:
            windowname (optional, str): Defines the window to get the position of. Defaults to "Doomstein98 - Google Chrome".
        
        Returns:
            region (tuple): Contains edges of the window

        Test:
            Create testwindow of specific size with f.e. opencv in top left corner of the desktop. Manually calculate region. Assert if the result of the function is equal.
            only test transormation from xyvz to xywh

        Sources:
            see [1]
        """
        self.logger.info("getWindowPosition: Getting window and xywh-pixels...")
        # Search window by name and get hWnd number
        hWnd = win32gui.FindWindow(None, windowname)
        # Get windows size of element with hWnd
        windowrect = win32gui.GetWindowRect(hWnd)
        # Convert xyvz to xywh
        #   windowcoords[0] --> x = windowrect[0]
        #   windowcoords[1] --> y = windowrect[1]
        #   windowcoords[2] --> w = windowrect[2] - windowrect[0]
        #   windowcoords[3] --> h = windowrect[3] - windowrect[1]
        region = windowrect[0], windowrect[1], windowrect[2] - windowrect[0], windowrect[3] - windowrect[1]
        self.logger.debug(f"getWindowPosition: windowrect (xyvz): {windowrect} --> region (xywh): {region}")
        self.logger.info("getWindowPosition: done")
        return region

    def getScreenshotOfWindow(self, region):
        """Screenshots the game

        Args:
            region (_type_): Pixel region where the game is on the desktop.

        Returns:
            numpyimage (image): Screenshotted image of the game.
        
        Tests:
            Use a test window as before screenshot and assert if frame exists.
            Check for frame format. F.e. is height and width none.
        
        Sources:
            see [1]
        """
        self.logger.info("getScreenshotOfWindow: Screenshotting frame...")
        # Screenshots the area defined ba region (xywh)
        frame = np.array(pyautogui.screenshot(region=region))
        # retrieve height, width from frame
        frameheight, framewidth = frame.shape[:2]
        self.logger.info("getScreenshotOfWindow: done")
        return frame, frameheight, framewidth

    def calculatePositionOfClosestPlayer(self, detections, framesize:tuple, fovoffsetx:float=1, fovoffsety:float=1):
        """Calculate which bounding box is closest to the crosshair.

        Args:
            detections (List): Bounding boxes of detected players.
            framesize (tuple): Height and width of the captured frame (width, height).
            fovoffsetx (optional, float): The discreptancy of the x-position of the player and the actual position of the pixel. Defaults to 1.
            fovoffsety (optional, float): The discreptancy of the y-position of the player and the actual position of the pixel. Defaults to 1.

        Returns:
            x (int): X-pixel of the players position
            y (int): Y-pixel of the players position
        
        Tests:
            Define array of detections. And see if the function returns the box closest to the center.
            Scenarios:
            - Two equally close boxes to the center --> last box in array should be returned
            - Many close boxes to the center --> shoud result in closest box to the center
            - A box over the center --> shoud result in closest box to the center
            - Many far away boxes --> shoud result in closest box to the center

        Sources:
            see [1]
        """
        self.logger.info("calculatePositionOfClosestPlayer: Searching closest bounding box to crosshair...")
        # Set first bbox as closest
        closestbbox = detections[0]
        self.logger.debug(f"calculatePositionOfClosestPlayer: Closest box: {closestbbox}")
        # Calculate distance with (( framew/2 - bboxwith/2)^2 + ( frameheight/2 - bboxheight/2 ))^1/2
        closestbboxdistance = math.sqrt(math.pow(framesize[0]/2 - (closestbbox[2][0]+closestbbox[2][2]/2), 2)+ 
                                        math.pow(framesize[1]/2 - (closestbbox[2][1]+closestbbox[2][3]/2), 2))
        # Search for closest bbox
        for bbox in detections:
            # xywh of bbox 
            (x, y, w, h) = bbox[2]
            # Calculate distance with (( framew/2 - bboxwith/2)^2 + ( frameheight/2 - bboxheight/2 ))^1/2
            disttocrosshair =  math.sqrt(math.pow(framesize[0]/2 - (x+w/2), 2) + math.pow(framesize[1]/2 - (y+h/2), 2))
            # Compare distances
            if closestbboxdistance > disttocrosshair:
                self.logger.debug(f"calculatePositionOfClosestPlayer: bbox: {bbox}, disttocrosshair: {disttocrosshair}, closestbboxdistance: {closestbboxdistance}, bool: {disttocrosshair < closestbboxdistance}")
                closestbbox = bbox
        self.logger.info(f"calculatePositionOfClosestPlayer: The bbox has: {closestbbox}. done")

        self.logger.info("calculatePositionOfClosestPlayer: Claculating the player position...")
        # Calculating the x,y-position of the player
        playerpositionx = int((closestbbox[2][0]+closestbbox[2][2]/2) * fovoffsetx)
        playerpositiony = int((closestbbox[2][1]+closestbbox[2][3]/2) * fovoffsety)
        self.logger.info(f"calculatePositionOfClosestPlayer: The playerposition is {playerpositionx}, {playerpositiony}. done")
        
        return playerpositionx, playerpositiony

    def moveMouseAndShoot(self, x:int, y:int, xwindow:int, ywindow:int):
        """Moves the mouse to the player and shoots

        Args:
            x (int): X-position of the player.
            y (int): Y-position of the player.

        Tests:
            Move mouse and check if the position has changed.
            Scenarios:
            - Move mouse out of desktop
            - Move mouse to non existent pixels
            - Move mouse to two points and assert if distance quals the manually calculated distance

        Sources:
            see [1]
        """
        self.logger.info(f"moveMouseAndShoot: Move mouse to {xwindow+x}, {ywindow+y} and press...")
        # Move mouse to x,y-pixel
        win32api.SetCursorPos((xwindow+x, ywindow+y))
        # Press left mouse button
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 
                             0, 0)
        # release left mouse button
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 
                             0, 0)
        self.logger.info(f"moveMouseAndShoot: done")
        return

    def lockTargetandShoot(self):
        """Mouves mouse cursor to target and shoots

        Tests:
            Diffucult test because the results can vary because of the object detection with the cnn.
            Use test window with test.jpg. Check if the cursor moved inside the space of the closest person (very time consuming).
            But that will not solve the problem that this test could fail anyway because the cnn does not detect the person.
        """
        # Get windowpos
        try:
            region = self.getWindowPosition(self.windowname)
        except:
            self.logger.warning(f"lockTargetandShoot: Cannot locate window with {self.windowname}.")
            return
        # Get frame
        frame, fw, fh = self.getScreenshotOfWindow(region)
        # Run object detection
        detections, frame = self.objectdetector.detectplayers(frame)
        # show
        if self.debug:
            cv2.imshow("Detected Frame", frame)
            cv2.waitKey(120)
        # Return if nothing was detected
        if len(detections) <= 0: return
        # Calculate closest player
        x, y = self.calculatePositionOfClosestPlayer(detections=detections, framesize=(fw, fh), 
                                                     fovoffsetx=self.fovoffsetx, fovoffsety=self.fovoffsety)
        self.moveMouseAndShoot(x, y, region[0], region[1])
        return
