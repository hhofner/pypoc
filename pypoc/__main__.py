'''
Main entry script for PyPoc. Reads the config and
creates & runs a Network.
'''
import network
import toml
import argparse
import plotter
import shutil
from pathlib import Path
from datetime import datetime, timedelta

__author__ = 'Hans Hofner'


parser = argparse.ArgumentParser()

parser.add_argument('--plot', action='store_true', help='Plot topology of all config files.')

parser.add_argument('--run', action='store_true', help='Run a simulation.')
parser.add_argument('--config', default='config.toml', help='Specific configuration file, optional.')

args = parser.parse_args()
configuration = toml.load(args.config)

if args.run:
    title = configuration["title"]
    # Copy file
    shutil.copyfile(args.config, f'./simulation_data/{title}.toml')
    # Create simulation data file
    # data_filename = f'{title}_{datetime.now().strftime("%d%b%y_%H_%M_%S")}.csv'
    data_filename = f'{title}.csv'
    Path('./simulation_data/'+data_filename).touch()

    new = network.PyPocNetwork()
    new.run_network_with(configuration, **{'filename': data_filename})
elif args.plot:
    raise Exception('Not yet implemented')
