""" Simple utilities used for debugging, logging, profiling, testing, etc. """

import datetime
import logging

# setup logger
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
LOGFILE_NAME = '{}.log'.format("test")  # TODO: Set this to correct format when logging
# prints log to stdout and also saves to specified log file
logger = logging.getLogger('my_logfile')
fh = logging.FileHandler(LOGFILE_NAME)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# ## UNCOMMENT BELOW FOR STDOUT
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# logger.addHandler(ch)
# ##############################
# set the logging level here
logger.setLevel(logging.DEBUG)
# for print message
DEBUG = True  # set this flag True to toggle DEBUG
VERBOSE = True  # set the flag to True for verbose


def get_now():
    """ Get a str of current time"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ## Trivial utils
def print_debug(msg):
    """ Logging and stuff """
    # logger.debug(msg)
    if DEBUG:
        print("DEBUG:", msg)


def print_info(msg: str):
    logger.info(msg)
    if VERBOSE:
        print("UPDATE:", msg)


def get_dict_str(d: dict) -> str:
    """ Given a dictionary, give a str output of key and value """
    return str({str(u): str(v) for u, v in d.items()})


def get_itr_str(iterable) -> str:
    """ Given a list, set or tuple returns str of values """
    return str([str(i) for i in iterable])
