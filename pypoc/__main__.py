'''
Main entry script for PyPoc. Reads the config and 
creates & runs a Network.
'''

__author__ = 'Hans Hofner'
import configparser

import network
import topology
import networkplotter

# Read Configuration File
# TODO: Config reading and passing arguments
from configparser import ConfigParser
parser = ConfigParser()
parser.read('setup.ini')

network = network.PyPocNetwork()
kwargs = {'threshold_value': 62500}
network.run_network(minutes=15, structure=topology.linear, 
                    bandwidth=1e3, src_node_count=2,
                    relay_node_count=None, relay_node_count2=None, 
                    dest_node_count=None, packet_size=500, **kwargs)