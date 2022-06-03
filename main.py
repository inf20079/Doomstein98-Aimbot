""" Main class
* Runs the Aimbot with parameters.

author: inf20079@lehre.dhbw-stuttgart.de
dat: 03.05.2022
version: 0.0.1
license: MIT

"""

import argparse
import logging
from modules.aimbot import Aimbot
from modules.object_detector_opencv import ObjectDetector
from time import sleep
from sys import stdout
import keyboard
from cv2 import destroyAllWindows
from os import mkdir

def parseArgs():
    """ Parses input arguments and saves them into a dict.

    Returns:
        dict: Script input arguments.

    Tests:
        Call function and assert if the dict contains a value for every parameter.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-cfg", "--config",
                        dest='config', # Variable name
                        type=str,
                        default="./cfg/object_detector.cfg",
                        required=False,
                        help="Path to the .cfg file containing the config of the network"),
    parser.add_argument("-lt", "--logging_type", # argument names
                        dest='logging_type', # Variable name
                        type=str,
                        default="central", # default value
                        required=False,
                        help="Sets the desired logging mode. Possible types are central (one log file for all classes) and decentral (every class has its own log file). This parameter is optional (standart central).") # help text
    parser.add_argument("-dbg", "--debug_flag", # argument names
                        dest='debug_flag', # Variable name
                        type=bool, # input type
                        default=True, # default value
                        required=False,
                        help="Flag that turns on the debug mode. The value has to be a boolean value. This parameter is optional.") # help text
    parser.add_argument("-wdn", "--window_name", # argument names
                        dest='window_name', # Variable name
                        type=str, # input type
                        default="The Different Ways People Walk. - YouTube - Google Chrome", # default value
                        required=False,
                        help="The window name of the game where the aimbot should run. The value has to be a string value. This parameter is optional.") # help text
    parser.add_argument("-fovx", "--fovoffsetx", # argument names
                        dest='fovoffsetx', # Variable name
                        type=float, # input type
                        default=0.9, # default value
                        required=False,
                        help="The value to correct distortion in the x axis. The value has to be a float value. This parameter is optional.") # help text
    parser.add_argument("-fovy", "--fovoffsety", # argument names
                        dest='fovoffsety', # Variable name
                        type=float, # input type
                        default=0.8, # default value
                        required=False,
                        help="The value to correct distortion in the y axis. The value has to be a float value. This parameter is optional.") # help text
    parser.add_argument("-llvl", "--logging_level", # argument names
                        dest='logging_level', # Variable name
                        type=str,
                        default="debug", # default value
                        required=False,
                        help="Sets the desired logging level of the logger. Possible types are debug and info. This parameter is optional (standart level info).") # help text
    args = parser.parse_args()
    return args

def create_logger(logging_level, debug = False):
    """ Creates a logger object which saves logs in file and outputs it to stdout.

    Args:
        logging_level (str): Logging level can be debug, info or error.
        debug (bool, optional): If true sets logging level to debug. Defaults to False.

    Returns:
        Logger: Logger object used for outputting logging messages

    Tests:
        check if logger object is created
        test logging functionality
        Scenarios:
        - create error log --> assert if message is in file
        - create info log --> assert if message is in file
        - create debug log --> assert if message is in file
    """
    # Set logging level
    if debug or logging_level == "debug":
        logging_level = logging.DEBUG
    elif logging_level == "error":
        logging_level = logging.ERROR
    else:
        logging_level = logging.INFO

    # Get logger
    logger = logging.getLogger(name="central_logger")
    # Set level
    logger.setLevel(logging_level)
    # create formatter
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    # logging file name
    name = './log/central_log.log'
    # Logging file handler
    try:
        file_handler = logging.FileHandler(filename=name, mode="a+")
    except:
        mkdir("./log")
        file_handler = logging.FileHandler(filename=name, mode="a+")
    file_handler.setFormatter(formatter)
    # Console handler
    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(formatter)
    # Add components
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def main():
    # Get input arguments
    args = parseArgs()

    # Create logger
    if args.logging_type == "central":
        logger = create_logger(args.logging_level)
    else:
        logger = None
    # Create object detector
    objectdetector = ObjectDetector(logger=logger, debug=args.debug_flag)
    # Create aimbot object
    aimbot = Aimbot(objectdetector, args.debug_flag,
                    args.window_name, args.fovoffsetx, 
                    args.fovoffsety, logger)

    logger.info("main: Aimbot started initialized. Press + to start. Afterwards press and hold + to quit.")
    while True:
        if keyboard.is_pressed("+"):
            logger.info("main: Starting...")
            break

    while True:
        aimbot.lockTargetandShoot()
        # Exit if + is pressed
        if keyboard.is_pressed("+"):
            logger.info("main: Exiting...")
            break

    # close opencv windows if in debug mode
    destroyAllWindows()

if __name__ == "__main__":
    main()