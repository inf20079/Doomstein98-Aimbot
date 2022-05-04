""" Main class
* Runs the Aimbot with parameters.

author: inf20079@lehre.dhbw-stuttgart.de
dat: 03.05.2022
version: 0.0.1
license: MIT

"""

import argparse
import logging
import datetime
import modules.aimbot
import modules.object_detector
from time import sleep

def parseArgs():
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
                        default=False, # default value
                        required=False,
                        help="Flag that turns on the debug mode. The value has to be a boolean value. This parameter is optional.") # help text
    parser.add_argument("-wdn", "--window_name", # argument names
                        dest='window_name', # Variable name
                        type=str, # input type
                        default="Doomstein98 - Google Chrome", # default value
                        required=False,
                        help="The window name of the game where the aimbot should run. The value has to be a string value. This parameter is optional.") # help text
    parser.add_argument("-fovx", "--fovoffsetx", # argument names
                        dest='fovoffsetx', # Variable name
                        type=float, # input type
                        default=1, # default value
                        required=False,
                        help="The value to correct distortion in the x axis. The value has to be a float value. This parameter is optional.") # help text
    parser.add_argument("-fovy", "--fovoffsety", # argument names
                        dest='fovoffsety', # Variable name
                        type=float, # input type
                        default=1, # default value
                        required=False,
                        help="The value to correct distortion in the y axis. The value has to be a float value. This parameter is optional.") # help text
    parser.add_argument("-llvl", "--logging_level", # argument names
                        dest='logging_level', # Variable name
                        type=str,
                        default="info", # default value
                        required=False,
                        help="Sets the desired logging level of the logger. Possible types are debug and info. This parameter is optional (standart level info).") # help text
    args = parser.parse_args()
    return args

def create_logger(logging_level, debug = False):
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
    name = './log/central_log'+str(datetime.now())+'.log'
    # Logging file handler
    file_handler = logging.FileHandler(name)
    file_handler.setFormatter(formatter)
    # Add components
    logger.addHandler(file_handler)
    return logger


def main():
    args = parseArgs()

    # Create logger
    if args.logging_type == "central":
        logger = create_logger(args.logging_level)
    else:
        logger = None
    # Create object detector
    objectdetector = modules.object_detector.ObjectDetector(args.config, logger, args.debug_flag)
    # Create aimbot object
    aimbot = modules.aimbot.Aimbot(objectdetector, args.window_name, 
                                   args.fovoffsetx, args.fovoffsety, logger)

    while True:
        aimbot.lockTargetandShoot()
        sleep(0.1)


if __name__ == "__main__":
    main()