import os
import csv
import time
import logging
from collections import defaultdict

import toml
import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pypoc.topology import Topology

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_network_graph(config_filepath=None):
    #TODO: Make more general
    if config_filepath is None:
        config_filepath = 'config.toml'

    configuration = toml.load(config_filepath)

    LOGGER.debug(f"Config file path: {config_filepath}")
    new = Topology(configuration)
    if len(new.topology) == 0:
        print(f'No edges created for this graph.')
        return

    temp_graph = nx.DiGraph(new.topology)
    node_colors = []
    node_sizes = []
    positions= {}
    for node in temp_graph.nodes:
        positions[node] = [float(node.position[0]), float(node.position[1])]
        if node.name == 'src-nodes':
            node_colors.append('royalblue')
            node_sizes.append(150)
        if node.name == 'dest-nodes':
            node_colors.append('firebrick')
            node_sizes.append(150)
        if node.name == 'base-stations':
            node_colors.append('goldenrod')
            node_sizes.append(450)
        if node.name == 'uav-base-stations':
            node_colors.append('darkgreen')
            node_sizes.append(360)
        if node.name == 'leo-satellites':
            node_colors.append('orchid')
            node_sizes.append(560)
        if node.name == 'q-stations':
            node_colors.append('brown')
            node_sizes.append(480)
    nx.draw_networkx(temp_graph, node_color=node_colors, pos=positions, arrows=True, with_labels=False, node_size=node_sizes)
    #nx.draw_networkx_nodes(temp_graph, node_color=node_colors, pos=positions, node_size=node_sizes)

    patches = []
    patches.append(mpatches.Patch(color='royalblue', label='Source UE\'s'))
    patches.append(mpatches.Patch(color='firebrick', label='Destination UE\'s'))
    patches.append(mpatches.Patch(color='goldenrod', label='Base Station\'s'))
    patches.append(mpatches.Patch(color='darkgreen', label='UAV Base Station\'s'))
    patches.append(mpatches.Patch(color='orchid', label='LEO Satellite\'s'))
    patches.append(mpatches.Patch(color='brown', label='Q-Station\'s'))
    plt.legend(handles=patches)
    plt.show()

if __name__ == '__main__':

    plot_network_graph()
