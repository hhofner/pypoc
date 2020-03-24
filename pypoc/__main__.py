'''
Main entry script for PyPoc. Reads the config and 
creates & runs a Network.
'''
import network
import toml
import argparse

__author__ = 'Hans Hofner'

parser = argparse.ArgumentParser()
parser.parse_args()

parser.add_argument('-p', '--plot', help='Plot most recent simulation run or passed .csv file.')  #TODO:

configuration = toml.load('config.toml')

new = network.PyPocNetwork()
new.run_network_with(configuration)