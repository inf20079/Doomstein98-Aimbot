"""Object detector class
* Loads Darknet framework and cnn. Runs as seperate thread and detects playermodels and returns the image with bounding boxes. 

author: inf20079@lehre.dhbw-stuttgart.de
dat: 03.05.2022
version: 0.0.1
license: MIT

"""

from datetime import datetime
import logging
import cv2
from threading import Thread
import os
import sys
import configparser


class ObjectDetector(Thread):
    """Object detector class that detects players and returns bounding boxes

    Inherits:
        Thread (Class): Threading class.
    """
    def __init__(self, cfg_file=None, logger=None, debug=False):
        
        # Create variables
        if cfg_file == None:
            self.cfg_file = os.getcwd() + "./cfg/object_detection.cfg"
        else: 
            self.cfg_file = cfg_file

        if not debug:
            self.debug = False
        else: 
            self.debug = debug

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

        # Loading neural network
        self.logger.info("Loading CNN...")

        # Load the configuration file
        self.logger.debug(f"Using cfg file: {self.cfg_file}")
        
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(self.cfg_file)

        # read from configuration file
        darknet_cfg_path = config.get("CNN", "cfg")
        darknet_data_path = config.get("CNN", "data")
        darknet_weights_path = config.get("CNN", "weights")

        # dynamically import darknet
        sys.path.insert(1, config.get("framework", "path"))
        self.darknet = __import__("darknet")
        
        # load CNN
        
        self.network, self.class_names, self.class_colors = self.darknet.load_network(
            darknet_cfg_path,
            darknet_data_path,
            darknet_weights_path,
            batch_size=1
        )
        self.logger.info("CNN loaded.")

        # Darknet doesn't accept numpy images.
        # Create darknet image object to store for detection
        self.width = self.darknet.network_width(self.network)
        self.height = self.darknet.network_height(self.network)
        self.darknetimage = self.darknet.make_image(self.width, self.height, 3)

    def convertNpimgToDnimg(self, numpyimage):
        """Converts the given numpy image to a darknet image.

        Args:
            numpyimage (image): Numpy image.

        Returns:
            darknetimage (image): Darknet image.
        """
        self.logger.info("convertNpimgToDnimg: Converting numpy image darknet image...")
        # Convert image to RGB if necessary
        numpyimage = cv2.cvtColor(numpyimage, cv2.COLOR_BGR2RGB)
        # Resize the image to the network size
        numpyimage = cv2.resize(numpyimage, (self.width, self.height),
                                interpolation=cv2.INTER_LINEAR)
        # Copy resized image to darknetimage
        self.darknet.copy_image_from_bytes(self.darknet_image, numpyimage.tobytes())
        self.logger.info("convertNpimgToDnimg: done")
        return self.darknetimage

    def detectplayers(self, thresh:float=0.5):
        """Runs the detection on the darknet image.

        Args:
            thresh (float, optional): Defines the confidence threshhold. Defaults to 0.5.

        Returns:
            array: Detected bounding boxes
        """
        # run image detection
        self.logger.info("detectplayers: Running Object detection...")
        # Run the detection on darknet
        detections = self.darknet.detect_image(self.network, self.class_names, self.darknet_image, thresh=thresh)
        # free the darknet image
        self.darknet.free_image(self.darknet_image)
        self.logger.info("detectplayers: done")
        return detections

    def resizeDetectionsToOriginalSize(self, detections):
        """Resize the detected bounding boxes from net size to original size.

        Args:
            detections (array): Detected bounding boxes from cnn

        Returns:
            array: Detected bounding boxes resized to original size
        """
        self.logger.info("resizeDetectionsToOriginalSize: Resizing detections...")
        # reshape bounding boxes to original image
        h, w, c = image_resized.shape
        h1, w1, c = image.shape
        h = (h1/h)
        w = (w1/w)

        # TODO: make loop to convert them to original size

        self.logger.info("resizeDetectionsToOriginalSize: done")
        return detections

    def run(self):
        """Runs the Yolov4 cnn and returns the detected bounding boxes.

        Args:
            image (image): The image in which objects are to be detected.
            thresh (float, optional): The confidence threshhold. Defaults to 0.5.

        Returns:
            image: Image with detected players.
            array: Array of detected bounding boxes.
        """

        # insert boundingboxes into image
        if self.debug:
            image = self.darknet.draw_boxes(detections, image, self.class_colors)
      
        return image, detections
