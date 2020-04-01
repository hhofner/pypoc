'''
Plotting module. Also to be able to be run from the command
line passing in Pickle files as arguments.
'''

__author__ = 'Hans Hofner'

import os
import csv
import datetime

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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
            
            ax.bar(bars.keys(), bars.values())
    
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
        
        width = 0.7
        indices = np.arange(len(generated_values))
        plt.bar(indices, generated_values, width=width, color='b', label='Number of generated packets.')
        plt.bar(indices, arrived_values, width=width, color='g', alpha=0.5, label='Number of arrived packets.')
        plt.bar(indices, dropped_values, width=width, color='r', alpha=0.5, label='Number of dropped packets.')

        plt.xticks(indices, more_filepaths )
        plt.legend()
    plt.show()