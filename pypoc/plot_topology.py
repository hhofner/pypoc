'''
Visual plotting script for topology.
'''
import argparse

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from topology import Topology


def plot_network_graph(config_filepath=None):
    #TODO: Make more general
    if config_filepath is None:
        config_filepath = 'config.toml'

    new = Topology(config_filepath)
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
    #nx.draw_networkx(temp_graph, node_color=node_colors, pos=positions, arrows=True, with_labels=True, node_size=node_sizes)
    nx.draw_networkx(temp_graph, node_color=node_colors, arrows=True, pos=positions, node_size=node_sizes, with_labels=False)

    patches = []
    patches.append(mpatches.Patch(color='royalblue', label='Source UE\'s'))
    patches.append(mpatches.Patch(color='firebrick', label='Destination UE\'s'))
    patches.append(mpatches.Patch(color='goldenrod', label='Base Station\'s'))
    patches.append(mpatches.Patch(color='darkgreen', label='UAV Base Station\'s'))
    patches.append(mpatches.Patch(color='orchid', label='LEO Satellite\'s'))
    plt.legend(handles=patches)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot topology "
            "of given config file")

    parser.add_argument('config', metavar='config', type=str,
            help='toml config file')

    args = parser.parse_args()
    plot_network_graph(args.config)

