'''
Main entry script for PyPoc. Reads the config and 
creates & runs a Network.
'''
import network
import toml
import argparse
import plotter

__author__ = 'Hans Hofner'

parser = argparse.ArgumentParser()

parser.add_argument('--plot', action='store_true', help='Plot most recent simulation run or passed .csv file.')
parser.add_argument('--run', action='store_true', help='Title of simulation run.')

args = parser.parse_args()

configuration = toml.load('config.toml')

if args.run:
    new = network.PyPocNetwork()
    new.run_network_with(configuration)
elif args.plot:
    plotter.plot()