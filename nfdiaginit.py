import argparse
import json
import os
import logging
import sys
from sys import platform

if platform != "win32":
    cur_path = os.path.dirname(__file__)
else:
    cur_path = os.getcwd()


# initiate the parser
def get_args():
    """

    :return:
    """
    parser = argparse.ArgumentParser(description='Cross platform nfdiag log parser', prog='nfdiag.py')
    parser.add_argument("-v", "--version", help="show program version", action='version', version='%(prog)s 0.8')
    parser.add_argument("file", type=str, metavar='File', nargs=1, help="<nfdiag-file>")
    parser.add_argument("-a", "--archive", type=int, metavar='Days', nargs='?', default=31, const=31,
                        help="Number of archive days to search")
    parser.add_argument("-d", "--debug", help="Debug logging level", action="store_true")
    parser.add_argument("-s", "--statistics", help="Show historical statistics", action="store_true")
    args = parser.parse_args()

    return args


def logs():
    """

    :return:
    """

    fmtstr = "%(levelname)s [%(asctime)s] file=%(filename)s function=%(funcName)s pid=[%(process)d] \
    %(processName)s line=%(lineno)d message=%(message)s"

    args = get_args()

    # custom logging config
    if args.debug:
        verbosity = logging.DEBUG
    else:
        verbosity = logging.INFO

    # Create a custom logger
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        # Here I created handler, formatter, loglevel etc..

        # Create handlers
        f_handler = logging.FileHandler('nfdiag.log')
        f_handler.setLevel(verbosity)

        # Create formatters and add it to handlers
        f_format = logging.Formatter(fmtstr)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(f_handler)
        logger.debug(args)
        logger.info("{0}, {1}, {2}".format(sys.executable, sys.argv[0], sys.argv[1:]))
    return logger, verbosity


def setup_logging(
        default_path='/json/logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


class NfDiag:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BColours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CLEARSCREEN = '\033[2J'


# noinspection PyPep8
class Status:
    # logging.debug("Printing status")
    def __init__(self, item, left=70, middle=70, right=5):
        self.left = left
        self.middle = middle
        self.right = right
        self.item = item

    # noinspection PyCompatibility
    def ok(self):
        # ok = "\'{:{0}}\'.format(item) + \'{:{1}}\'.format(\'\n\') + \
        #      \'{:{2}}\'.format(f\"{BColours.FAIL}[NOK]{BColours.ENDC}\"))"
        print('{:70}'.format(self.item) + '{:70}'.format("\n") +
              '{:5}'.format(f"{BColours.OKGREEN}[OK]{BColours.ENDC}"))
        # return ok.format(self.left, self.middle, self.right)

    # noinspection PyCompatibility,PyPep8
    def nok(self):
        # nok = "\'{:{0}}\'.format(item) + \'{:{1}}\'.format(\'\n\') + \
        #      \'{:{2}}\'.format(f\"{BColours.FAIL}[NOK]{BColours.ENDC}\"))"
        # print("\'{:" + str(self.left) + "}\'".format(self.item))
        print('{:70}'.format(self.item) + '{:70}'.format("\n") + '{:5}'.format(f"{BColours.FAIL}[NOK]{BColours.ENDC}"))
        #   + '{:' + str(self.right) + '}'.format("[NOK]")
        # print(nok)
        # return nok
