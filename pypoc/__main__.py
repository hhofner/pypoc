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
    # TODO: Distribute plotting actions -- if more than one (other than all) are speicifed, plot them.
    if args.all:
        plotter.plot_all()
    elif args.packets:
        if args.datafile:
            plotter.plot_packet_simple(more_filepaths=[args.datafile, args.datafile2, args.datafile3, args.datafile4])
        else:
            plotter.plot_packet_simple()
    elif args.queue:
        if args.datafile:
            plotter.plot_queue_simple(more_filepaths=[args.datafile, args.datafile2, args.datafile3, args.datafile4])
        else:
            plotter.plot_queue_simple()
    elif args.throughput:
        plotter.plot_throughputs()
    elif args.droprate:
        plotter.plot_drop_rate()
    elif args.topology:
        plotter.plot_network_graph(configuration)
