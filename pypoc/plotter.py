'''
Plotting module. Also to be able to be run from the command
line passing in Pickle files as arguments.
'''

__author__ = 'Hans Hofner'

import os
import csv
import datetime

import seaborn as sns
import matplotlib.pyplot as plt

# sns.set()
# sns.set_style('whitegrid')
def plot(filepath=None, sim_directory='./simulation_data'):
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
                    filepath = temp_filepath
                elif os.path.getmtime(temp_filepath) > os.path.getmtime(filepath):
                    filepath = temp_filepath
    else:
        if not os.path.isfile(filepath):
            raise Exception(f'`{filepath}` is not a valid filepath.')

    # fig_shapes = [()]

    will_plot = {'queue_size': True, 'packet_stats': True}

    fig, ax = plt.subplots(1,2)   

    with open(filepath, mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # data = []
        for row in reader:
            if will_plot['queue_size']:
                queue_length_data_to_plot = []
                if 'rel_queue_size' in row[0]:
                    for data_point in row[1:]:
                        queue_length_data_to_plot.append(int(data_point))
                    ax[0].plot(queue_length_data_to_plot, label=row[0])
            if will_plot['packet_stats']:
                pass

            # if 'throughput_list' in row[0]:
            #     for data_point in row[1:]:
            #         data_to_plot.append(float(data_point))
            #     ax.plot(data_to_plot, label=row[0])

    graphs_to_plot = []

    plt.legend(loc='upper right')

    plt.show()