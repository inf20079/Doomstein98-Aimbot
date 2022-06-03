"""Object detector class
* Loads Darknet framework and cnn. Runs as seperate thread and detects playermodels and returns the image with bounding boxes. 

author: inf20079@lehre.dhbw-stuttgart.de
dat: 03.05.2022
version: 0.0.1
license: MIT

"""

import logging
import cv2
import numpy as np
import os
import configparser


class ObjectDetector():
    """Object detector class that detects players and returns bounding boxes
    """
    def __init__(self, cfg_file=None, logger=None, debug=False):
        """Initializes the ObjectDetector. Loads CNN.

        Args:
            cfg_file (cfg, optional): The Config file for the neural network. Defaults to None.
            logger (Logger, optional): Logger. Either giver or created by class. Defaults to None.
            debug (bool, optional): Debug mode logs additional information. Defaults to False.

        Tests:
            check if class can be instancianted
            check if cnn loads correctly
            Scenarios:
            - use correct config file
            - use wrong config file (file format or missing parameters)

        Sources:
            see [2]
        """
        # Create variables
        if cfg_file == None:
            self.cfg_file = os.getcwd() + "\cfg\object_detector.cfg"
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
            name = './log/object_detection.log'
            # Logging file handler
            file_handler = logging.FileHandler(name)
            file_handler.setFormatter(formatter)
            # Add components
            self.logger.addHandler(file_handler)
        else: 
            self.logger = logger

        self.originalheight = None
        self.originalwidth = None
        self.originalimage = None
        self.blobimage = None

        # Loading neural network
        self.logger.info("Loading CNN...")

        # Load the configuration file
        self.logger.debug(f"Using cfg file: {self.cfg_file}")
        
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(self.cfg_file)

        # read from configuration file
        cnn_cfg_path = config.get("CNN", "cfg")
        cnn_names_path = config.get("CNN", "names")
        cnn_weights_path = config.get("CNN", "weights")
        self.logger.debug(f"CNN config paths are: config={cnn_cfg_path}, weights={cnn_weights_path}, classes={cnn_names_path}")

        # read cnn params
        # input format for cnn
        self.cnn_param_width = int(config.get("PARAMETERS", "width"))
        self.cnn_param_height = int(config.get("PARAMETERS", "height"))

        # load net
        try:
            self.net = cv2.dnn.readNet(cnn_weights_path, cnn_cfg_path)
        except:
            self.logger.error(f"CNN cannot be loaded with cnn_weights_path={cnn_weights_path} and cnn_cfg_path={cnn_cfg_path}. Please check config file.")
            exit(1)

        # add classes
        self.classes = []
        with open(cnn_names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        # determine output layers
        layernames = self.net.getLayerNames()
        self.outputlayers = [layernames[i - 1] for i in self.net.getUnconnectedOutLayers()]

        self.logger.info("CNN loaded.")

    def convertimgToBlob(self, image):
        """Converts the given image to a blob.

        Args:
            image (image): A image to convert to blob.

        Returns:
            blob (image): A RGB blob compatible with opencv.

        Tests:
            convert different frames to blob
            Scenarios:
            - test image in blob and assert equals with predefined blob
            - try to convert a corrupt image and assert false
            - try to convert different frame formats to blob and assert if conversion successful
        
        Sources:
            see [2]
        """
        self.logger.info("convertimgToBlob: Converting numpy image darknet image...")
        # save original image for later use 
        self.originalimage = image
        # save original image size for resizing to original size 
        self.originalheight, self.originalwidth, channels = image.shape
        # Resize the image to the network size and convert to blob
        self.blobimage = cv2.dnn.blobFromImage(image, 0.00392, (self.cnn_param_height, self.cnn_param_width), (0, 0, 0), crop=False)
        return self.blobimage

    def resizeDetectionsToOriginalSize(self, detections, threshhold=0.5):
        """Resize the detected bounding boxes from net size to original size.

        Args:
            detections (list): Detected bounding boxes from cnn
            threshhold (float): Confidence threshhold. Defaults to 0.5.

        Returns:
            resizedboundingboxes (list): Detected bounding boxes resized to original size.
            labels (list): Labels of bounding boxes in the same order.
            conficences (list): Confidences of bounding boxes in the same order

        Tests:
            Predefine a set of unconverted boxes and converted boxes and assert if the result equals the converted boxes.
            Scenarios:
            - different frame sizes 
            - different box sizes
            Check if the function returns all three lists with their respective content (e.g. labels contains a set of strings)
            Scenarios:
            - Correct content --> assert true
            - False content --> assert false

        Source:
            see [2]
        """
        self.logger.info("resizeDetectionsToOriginalSize: Resizing detections...")
        # reshape bounding boxes to original image
        resizedboundingboxes = []
        conficences = []
        labels = []
        for detection in detections:
            for boundingbox in detection:
                # extract bounding box values
                scores = boundingbox[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]
                if confidence > threshhold:
                    self.logger.debug(f"resizeDetectionsToOriginalSize: Original boxes: [{boundingbox[0]}, {boundingbox[1]}, {boundingbox[2]}, {boundingbox[3]}]")
                    # Resize the bounding box to original size 
                    xcenter = int(boundingbox[0] * self.originalwidth)
                    ycenter = int(boundingbox[1] * self.originalheight)
                    width = int(boundingbox[2] * self.originalwidth)
                    height = int(boundingbox[3] * self.originalheight)
                    self.logger.debug(f"resizeDetectionsToOriginalSize: Resized boxes: [{xcenter}, {ycenter}, {width}, {height}]")
                    # append to resized bbox array
                    labels.append(str(self.classes[classid]))
                    conficences.append(confidence)
                    resizedboundingboxes.append([xcenter, ycenter, 
                                                 width, height])

        self.logger.info("resizeDetectionsToOriginalSize: done")
        return resizedboundingboxes, labels, conficences

    def mergeConvergingBoxes(self, boundingboxes:list, confidences:list, labels:list, threshhold:float=0.5, nmsthreshhold:float=0.4):
        """Merges converging bounding boxes.

        Args:
            boundingboxes (list): Bounding boxes to merge.
            confidences (list): Confidences of bounding boxes in the same order.
            labels (list): Labels of bounding boxes in the same order.
            threshhold (float): Confidence threshhold. Defaults to 0.5.
            nmsthreshhold (float): threshhold for convergence. Defaults to 0.4.

        Returns:
            nonconvergingboxes (list): Array of non converging bounding boxes with the following bbox format: [class, confidence [xcenter, ycenter, width, height]].
            originalimage (image): Image with drawn bounding boxes. If debug is enabled.

        Tests:
            Define a set of boxes and assert if output is as expected.
            Scenarios:
            - define set of boxes very close with the same label --> should be merged
            - define set of boxes very close with different labels --> should not be merged

        Source:
            see [2]
        """
        # remove converging bounding boxes
        self.logger.info(f"mergeConvergingBoxes: Removing converging boxes...")
        indexes = cv2.dnn.NMSBoxes(boundingboxes, confidences, threshhold, nmsthreshhold)
        self.logger.info(f"...done")

        self.logger.info(f"mergeConvergingBoxes: Merging lists...")
        nonconvergingboxes = []
        for count, index in enumerate(indexes):
            # Summarize to one array
            self.logger.debug(f"mergeConvergingBoxes: Summarize bbox: [{labels[index]}, {confidences[index]}, {boundingboxes[index]}]")
            nonconvergingboxes.append([labels[index], confidences[index], boundingboxes[index]])
            self.logger.debug(f"mergeConvergingBoxes: Summarized bbox: {nonconvergingboxes[count]}")

            if self.debug == False: continue
            
            # Draw bounding boxes on image for debug purposes
            # Compute top left corner
            x = int(nonconvergingboxes[count][2][0] - nonconvergingboxes[count][2][2] / 2)
            y = int(nonconvergingboxes[count][2][1] - nonconvergingboxes[count][2][3] /2)
            label = str(labels[index])
            confidence = str(confidences[index])
            # Draw rectangle
            cv2.rectangle(self.originalimage, (x, y), 
                          (x + nonconvergingboxes[count][2][2], y + nonconvergingboxes[count][2][3]), (255, 0 , 0), 2)
            # Draw label
            cv2.putText(self.originalimage, label, (x, y + 30),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 3)
            # Draw confidence
            cv2.putText(self.originalimage, confidence, (x, y + 50),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 3)
        self.logger.info(f"...done")
        
        self.logger.debug(f"mergeConvergingBoxes: Non converging bounding boxes: {nonconvergingboxes}")
        return nonconvergingboxes, self.originalimage

    def filterForPerson(self, detections:list):
        """ Filters list of detections for bboxes with person class

        Args:
            detections (list): List of all detections

        Returns:
            list: List of detected persons

        Tests:
            Define set of boxes with different labels and check if filtering was correct.
            Scenarios:
            - no box with class person --> empty list
            - boxes with persons --> output should be amount of defined boxes with class person
        """
        # Filter detections for person class
        persondetections = []
        for boundingbox in detections:
            if boundingbox[0] == "person":
                persondetections.append(boundingbox)
        
        return persondetections

    def detectplayers(self, frame, thresh:float=0.5, nmsthresh:float=0.4):
        """Runs the Yolov4 cnn and returns the detected bounding boxes.

        Args:
            frame (image): The image in which objects are to be detected.
            thresh (float, optional): The confidence threshhold. Defaults to 0.5.

        Returns:
            nonconvergingboxes (list): Array of detected person bounding boxes.
            frame (image): Image with detected players.

        Tests:
            Difficult to test because of the neural network. Output may vary with the same input.
            Possible test case: Use test.jpg and check if the center of the detected boxes are in the area of the persons in the picture.
            Easier test but not representative for the functionality of the function. Just test if there is a output.
        """
        # run image detection
        self.logger.info("detectplayers: Running Object detection...")
        # Resize image to network size 
        self.convertimgToBlob(frame)
        # Run the detection on darknet
        self.net.setInput(self.blobimage)
        detections = self.net.forward(self.outputlayers)
        # Resize the bounding boxes
        boundingboxes, labels, confidences = self.resizeDetectionsToOriginalSize(detections)
        # Merge converging boxes
        nonconvergingboxes, frame = self.mergeConvergingBoxes(boundingboxes, confidences, labels, thresh, nmsthresh)
        # Filter detections for persons
        detectedplayers = self.filterForPerson(nonconvergingboxes)
        # free the darknet image
        self.logger.info("detectplayers: done")
        return detectedplayers, frame