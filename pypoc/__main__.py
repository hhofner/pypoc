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
parser.add_argument('--all', action='store_true', help='Plot all stats.')
parser.add_argument('--queue', action='store_true', help='Plot analysis of number of packets in the queue.')
parser.add_argument('--packets', action='store_true', help='Plot generated/arrived/dropped packets bar chart.')
parser.add_argument('--datafile', nargs='*', help='Data files to plot.')

parser.add_argument('--run', action='store_true', help='Title of simulation run.')
parser.add_argument('--config', default='config.toml', help='Specific configuration file, optional.')

args = parser.parse_args()

configuration = toml.load(args.config)

if args.run:
    new = network.PyPocNetwork()
    new.run_network_with(configuration)
elif args.plot:
    # TODO: Distribute plotting actions -- if more than one (other than all) are speicifed, plot them.
    if args.all:
        plotter.plot_all()
    elif args.packets:
        if args.datafile:
            plotter.plot_packet_simple(more_filepaths=args.datafile)
        else:
            plotter.plot_packet_simple()
    elif args.queue:
        if args.datafile:
            plotter.plot_queue_simple(more_filepaths=args.datafile)
        else:
            plotter.plot_queue_simple()