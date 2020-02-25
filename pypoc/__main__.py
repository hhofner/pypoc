'''
Main entry script for PyPoc.
'''

import argparse
import configparser

from configparser import ConfigParser
parser = ConfigParser()
parser.read('setup.ini')

print(parser.get())