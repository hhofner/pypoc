'''
Plotting module.
'''

__author__ = 'Hans Hofner'

import os
import csv
import datetime

import numpy as np
import pandas as pd
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
        
        width = 0.7
        indices = np.arange(len(generated_values))
        plt.bar(indices, generated_values, width=width, color='b', label='Total packets.')
        plt.bar([i+0.25*width for i in indices], arrived_values, width=width, color='g', label='Arrived packets.')
        plt.bar([i+0.5*width for i in indices], dropped_values, width=width, color='r', label='Dropped packets.')

        plt.xticks(indices, more_filepaths)
        plt.legend()
    
    plt.show()

def plot_queue_simple(filepath=None, sim_directory='./simulation_data', more_filepaths=None, max_plots=1, restrained_time=False):
    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots()

    if more_filepaths:
        ''' Multiple plotting '''
        # First, collect all queue_l for one file
        #   calculate the average for all at every point
        # Then plot
        for filepath in more_filepaths:
            temp_data = []
            # Collect data
            with open(filepath, mode='r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    temp_row_data = []
                    if 'rel_queue' in row[0]:
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
        ''' Singular plotting '''
        filepath = get_filepath(filepath, sim_directory) # Get most recent
        times_plotted = 0
        with open(filepath, mode='r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if times_plotted >= max_plots:
                    break
                temp_ql_data = []
                if 'rel_queue' in row[0]:
                    for data_point in row[1:]:
                        temp_ql_data.append(int(data_point))
                    ax.plot(temp_ql_data, label=row[0])
                    times_plotted += 1
        plt.legend()
        ax.set_title('Number of packets in queues.')
        ax.set_xlabel('Ticks')
        ax.set_ylabel('Amount')

    plt.show()