'''
Plotting module.
'''

__author__ = 'Hans Hofner'

import os
import csv
import time
import datetime
from collections import defaultdict

import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from topology import Topology

def get_filepath(filepath=None, sim_directory='./simulation_data'):
    if filepath is None:
        if not os.path.isdir(sim_directory):
            raise Exception(f'{sim_directory} directory does not exist!')
        if not os.listdir(sim_directory):
            raise Exception(f'{sim_directory} directory is empty. Please run a simulation.')
        for file in os.listdir(sim_directory):
            temp_filepath = os.path.join(sim_directory, file)
            # Find most recent file
            if os.path.isfile(temp_filepath):
                if filepath is None:
                    filepath= temp_filepath
                elif os.path.getctime(temp_filepath) > os.path.getctime(filepath):
                    filepath= temp_filepath
        return filepath
        print(f'Plotting most recent file {filepath}')
    else:
        if not os.path.isfile(filepath):
            raise Exception(f'`{filepath}` is not a valid filepath.')

def get_datafiles_from_directory(directory_path):
    ''' Fetch all CSV files from the directory'''
    datafiles = []
    for file in os.listdir(directory_path):
        if os.path.isfile(os.path.join(file, directory_path)) and file[-3:] == 'csv':
            datafiles.append(os.path.join(file, directory_path))

    return datafiles


def plot_all(filepath=None, sim_directory='./simulation_data'):
    filepath = get_filepath(filepath, sim_directory)

    sns.set()
    sns.set_style('whitegrid')

    will_plot = {'queue_size': True, 'packet_stats': False}
    queue_size_count = 0

    fig_shapes = [(1,1), (1,2), (2,2), (2,3), (3,3)]
    fshape = sum(1 for key in will_plot if will_plot[key])
    # TODO: Need to assign axes to keys

    fig, ax = plt.subplots(fshape)

    with open(filepath, mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        number_of_queue_plots = 10

        for row in reader:
            # Queue Lengths
            temp_ql_data = []
            if 'rel_queue_size' in row[0]:
                for data_point in row[1:]:
                    temp_ql_data.append(int(data_point))
                if will_plot['queue_size'] and number_of_queue_plots > 0:
                    ax.plot(temp_ql_data, label=row[0])
                    number_of_queue_plots -= 1

            if will_plot['packet_stats']:
                pass

    plt.legend(loc='upper right')

    plt.show()

def plot_packet_simple(filepath=None, sim_directory='./simulation_data', more_filepaths=None):
    fig, ax = plt.subplots()

    sns.set()
    sns.set_style('whitegrid')

    # Plot singular
    if more_filepaths is None:
        filepath = get_filepath(filepath, sim_directory)
        with open(filepath, mode='r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            bars = {}
            for row in reader:
                if 'packet_generated_value' in row[0]:
                    generated_value = int(row[1])
                    bars['Generated'] = generated_value
                if 'packet_drop_value' in row[0]:
                    drop_value = int(row[1])
                    bars['Dropped'] = drop_value
                if 'packet_arrive_value' in row[0]:
                    arrive_value = int(row[1])
                    bars['Arrived'] = arrive_value

            ax.bar(bars.keys(), bars.values(), color=['r', 'g', 'b'])

    # Plot multiple
    else:
        generated_values = []
        arrived_values = []
        dropped_values = []
        for filepath in more_filepaths:
            with open(filepath, mode='r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    if 'packet_generated_value' in row[0]:
                        g_val = int(row[1])
                        generated_values.append(g_val)
                    if 'packet_drop_value' in row[0]:
                        d_val = int(row[1])
                        dropped_values.append(d_val)
                    if 'packet_arrive_value' in row[0]:
                        a_val = int(row[1])
                        arrived_values.append(a_val)

        width = 0.55
        indices = np.arange(len(generated_values))
        plt.bar(indices, generated_values, width=width, color='b', label='Total packets.')
        plt.bar([i+0.25*width for i in indices], arrived_values, width=width, color='g', label='Arrived packets.')
        plt.bar([i+0.5*width for i in indices], dropped_values, width=width, color='r', label='Dropped packets.')

        ax.set_title('Packet Information for Multiple Simulations')
        plt.xticks(indices, more_filepaths)
        plt.legend()

    plt.show()

def plot_queue_simple(filepath=None, sim_directory='./simulation_data', more_filepaths=None, restrained_time=False):
    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots()

    if more_filepaths:
        for file_set in more_filepaths:
            if file_set is None:
                continue
            ''' Multiple plotting '''
            # First, collect all queue_l for one file
            #   calculate the average for all at every point
            # Then plot
            for filepath in file_set:
                temp_data = []
                # Collect data
                with open(filepath, mode='r') as csvfile:
                    print(f'{">" * 30} Parsing file: {filepath} {">" * 30}')
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        temp_row_data = []
                        if 'rel' in row[0] and 'queue' in row[0]:
                            for data_point in row[1:]:
                                temp_row_data.append(int(data_point))
                            temp_data.append(temp_row_data)
                # Turn into DataFrame and compress columns into averages
                queue_df = pd.DataFrame(temp_data)
                averages = queue_df.mean().tolist()
                ax.plot(averages, label=filepath)
        plt.legend()
        ax.set_title('Average number of packets for all relay nodes per time.')
        ax.set_xlabel('Ticks')
        ax.set_ylabel('Amount')

    else:
        ''' Singular (Simulation) plotting '''
        filepath = get_filepath(filepath, sim_directory) # Get most recent
        print(f'Plotting for {filepath}')
        times_plotted = 0
        node_qlength = defaultdict(list)
        with open(filepath, mode='r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                temp_ql_data = []
                if 'queue_size' in row[0]:
                    if 'dest-nodes' in row[0] or 'src-nodes' in row[0]:
                        continue
                    node_name = row[0].split('_')[3]
                    for data_point in row[1:]:
                        temp_ql_data.append(int(data_point))
                    node_qlength[node_name].append(temp_ql_data)
        final_list = []
        # Go from dict to list
        for key in node_qlength.keys():
            temp_df = pd.DataFrame(node_qlength[key])
            averages = temp_df.mean().tolist()
            ax.plot(averages, label=key)
        plt.legend()
        ax.set_title('Average Number of packets in queues per time.')
        ax.set_xlabel('Ticks')
        ax.set_ylabel('Average Amount')

    plt.show()

def plot_throughputs():
    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots()

    dirpath = 'simulation_data/'
    sim_set = []
    for i in range(1, 5):
        filepaths = []
        for file in os.listdir(dirpath):
            if f'thu_t{i}' in file or f'thur_t{i}' in file:
                if '.csv' in file:
                    filepath = dirpath + file
                    filepaths.append(filepath)
        sim_set.append(filepaths)
    
    def get_num(x):
        return int(x.split('__')[1][:x.split('__')[1].index('.')])

    for fileset in sim_set:
        throughput_movement = []
        x_numbers = []
        for filepath in sorted(fileset, key=get_num):
            print(f'{">" * 15} parsing {filepath} {">" * 15}')

            with open(filepath, mode='r') as csvfile:
                reader=csv.reader(csvfile)
                for row in reader:
                    try:
                        if 'throughput_value' in row[0]:
                            throughput_movement.append(float(row[1])/8)
                            break
                    except IndexError:
                        input(f"IndexError for {filepath}: {row}")
                        raise
            x_numbers.append(get_num(filepath))
        plt.plot(x_numbers, throughput_movement, label=f't{sim_set.index(fileset)}')
    
    ax.set_title(f'Network Throughput')
    ax.set_ylabel(f'bits-per-second')
    plt.legend()
    plt.show()

def plot_drop_rate():
    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots()

    dirpath = 'i_gr_data/'; print(f'{"#"*25} Plotting from dir {dirpath}!!! {"#"*25}')
    time.sleep(2)

    sim_set = []
    for i in range(1, 5):
        filepaths = []
        for file in os.listdir(dirpath):
            if f'thu_t{i}' in file or f'thur_t{i}' in file:
                if '.csv' in file:
                    filepath = dirpath + file
                    filepaths.append(filepath)
        sim_set.append(filepaths)
    
    def get_num(x):
        return int(x.split('__')[1][:x.split('__')[1].index('.')])

    for fileset in sim_set:
        drop_rates = []
        x_numbers = []
        for filepath in sorted(fileset, key=get_num):
            print(f'{">" * 15} parsing {filepath} {">" * 15}')

            with open(filepath, mode='r') as csvfile:
                reader=csv.reader(csvfile)
                drop_value = None; generated_value = None
                for row in reader:
                    try:
                        if 'packet_drop_value' in row[0]:
                            drop_value = float(row[1])
                    except IndexError:
                        input(f"IndexError for {filepath}: {row}")
                        raise
                    try:
                        if 'packet_generated_value' in row[0]:
                            generated_value = float(row[1])
                    except IndexError:
                        input(f"IndexError for {filepath}: {row}")
                        raise
            
            drop_rates.append((drop_value/generated_value)*100)
                            
            x_numbers.append(get_num(filepath))
        plt.plot(x_numbers, drop_rates, label=f't{sim_set.index(fileset)}')
    
    ax.set_title(f'Drop Rate')
    ax.set_ylabel(f'Percentage %')
    plt.legend()
    plt.show()

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
            node_colors.append('blue')
            node_sizes.append(150)
        if node.name == 'dest-nodes':
            node_colors.append('red')
            node_sizes.append(150)
        if node.name == 'base-stations':
            node_colors.append('yellow')
            node_sizes.append(450)
        if node.name == 'uav-base-stations':
            node_colors.append('green')
            node_sizes.append(360)
        if node.name == 'leo-satellites':
            node_colors.append('brown')
            node_sizes.append(560)
    nx.draw_networkx(temp_graph, node_color=node_colors, pos=positions, arrows=True, with_labels=True, node_size=node_sizes)
    #nx.draw_networkx_nodes(temp_graph, node_color=node_colors, pos=positions, node_size=node_sizes)

    patches = []
    patches.append(mpatches.Patch(color='blue', label='Source UE\'s'))
    patches.append(mpatches.Patch(color='red', label='Destination UE\'s'))
    patches.append(mpatches.Patch(color='yellow', label='Base Station\'s'))
    patches.append(mpatches.Patch(color='green', label='UAV Base Station\'s'))
    patches.append(mpatches.Patch(color='brown', label='LEO Satellite\'s'))
    plt.legend(handles=patches)
    plt.show()

def save_network_graph_image(networkx_ob, filepath, **kwargs):

    plt.clf()

    node_colors = []
    node_sizes = []
    positions= {}
    for node in networkx_ob.nodes:
        positions[node] = [float(node.position[0]), float(node.position[1])]
        if node.name == 'src-nodes':
            node_colors.append('blue')
            node_sizes.append(150)
        if node.name == 'dest-nodes':
            node_colors.append('red')
            node_sizes.append(150)
        if node.name == 'base-stations':
            node_colors.append('yellow')
            node_sizes.append(450)
        if node.name == 'uav-base-stations':
            node_colors.append('green')
            node_sizes.append(360)
        if node.name == 'leo-satellites':
            node_colors.append('brown')
            node_sizes.append(560)
    nx.draw_networkx(networkx_ob, node_color=node_colors, pos=positions, arrows=True,
                     with_labels=True, node_size=node_sizes)

    patches = []
    patches.append(mpatches.Patch(color='blue', label='Source UE\'s'))
    patches.append(mpatches.Patch(color='red', label='Destination UE\'s'))
    patches.append(mpatches.Patch(color='yellow', label='Base Station\'s'))
    patches.append(mpatches.Patch(color='green', label='UAV Base Station\'s'))
    patches.append(mpatches.Patch(color='brown', label='LEO Satellite\'s'))

    plt.title(f'Tick {kwargs["tick_val"]}')
    plt.legend(handles=patches)
    plt.xlim(-100, 100)
    plt.ylim(-100, 100)
    plt.savefig(filepath)
    # plt.show()