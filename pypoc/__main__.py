'''
Main entry script for PyPoc. Reads the config and 
creates & runs a Network.
'''

import argparse
import configparser

from configparser import ConfigParser
parser = ConfigParser()
parser.read('setup.ini')

print(parser.get('nodes'))