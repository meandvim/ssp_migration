#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import inspect
sys.path.append("/usr/local/rootbin/Pythonlib/")
import amdisplay

logging.basicConfig(format='%(asctime)s %(message)s',
    level=logging.DEBUG,
    datefmt='## %d-%m-%Y %I:%M:%S ')


def pfn(verbose):
    """Prints the function name
    :v: verbose:
    """
    if verbose >= 2:
        logging.info("##Start of: ---( {} )---".format(inspect.stack()[1][3])) 
