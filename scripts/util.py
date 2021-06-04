import logging
import sys
import os
import argparse

# Logging config
def logging_setup(args=None):
    logger = logging.getLogger()
    logger.handlers = []  # Removing default handler to avoid duplication of log messages
    logger.setLevel(logging.ERROR)

    h = logging.StreamHandler(sys.stderr)
    if args != None:
        h = logging.StreamHandler(args.logfile)

    h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

    if args != None:
        if not args.quiet:
            logger.setLevel(logging.INFO)
        if args.debug:
            logger.setLevel(logging.DEBUG)

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue
