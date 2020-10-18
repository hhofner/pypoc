'''
Main entry script for PyPoc. Reads the config and
creates & runs a Network.
'''
import os
import toml
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta

import pypoc.network as network
import pypoc.plotter as plotter

__author__ = 'Hans Hofner'


parser = argparse.ArgumentParser()

parser.add_argument('--plot', action='store_true', help='Plot most recent simulation run or passed .csv file.')
parser.add_argument('--all', action='store_true', help='Plot all stats.')
parser.add_argument('--queue', action='store_true', help='Plot analysis of number of packets in the queue.')
parser.add_argument('--packets', action='store_true', help='Plot generated/arrived/dropped packets bar chart.')
parser.add_argument('--throughput', action='store_true', help='Plot the throughput of file(s).')
parser.add_argument('--droprate', action='store_true', help='Plot the drop rate of file(s).')
parser.add_argument('--progression', default=False, action='store_true')
parser.add_argument('--topology', action='store_true', help='Visual plot of topology.')
parser.add_argument('--datafile', nargs='*', help='Data files to plot.')
parser.add_argument('--datafile2', nargs='*', help='Data files to plot.', default=None)
parser.add_argument('--datafile3', nargs='*', help='Data files to plot.', default=None)
parser.add_argument('--datafile4', nargs='*', help='Data files to plot.', default=None)

parser.add_argument('--run', action='store_true', help='Run a simulation.')
parser.add_argument('--config', default='config.toml', help='Specific configuration file, optional.')
parser.add_argument('--output_dir', default='/Users/hhofner/Documents/PyPoc/output_data')

args = parser.parse_args()
configuration = toml.load(args.config)

if args.run:
    title = configuration["title"]
    # Copy file
    shutil.copyfile(args.config, f'{args.output_dir}/{title}.toml')
    # Create simulation data file
    data_filename = f'{title}_{datetime.now().strftime("%d%b%y_%H_%M_%S")}.csv'
    # data_filename = f'{title}.csv'
    Path(f'{args.output_dir}/'+data_filename).touch()

    new = network.PyPocNetwork()
    new.run_network_with(configuration, **{'filename': data_filename})
