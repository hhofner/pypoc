'''
Plotting module. Also to be able to be run from the command
line passing in Pickle files as arguments.
'''

__author__ = 'Hans Hofner'

import matplotlib.pyplot as plt
import seaborn as sns
import csv

# sns.set()
# sns.set_style('whitegrid')

fig_shapes = [()]

will_plot = {'queue_size': True, 'packet_stats': True}

filename = '../test.csv'

fig, ax = plt.subplots(1,2)   

with open(filename, mode='r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    # data = []
    for row in reader:
        if will_plot['queue_size']:
            queue_length_data_to_plot = []
            if 'rel_queue_size' in row[0]:
                for data_point in row[1:]:
                    queue_length_data_to_plot.append(int(data_point))
                ax[0].plot(data_to_plot, label=row[0])
        if will_plot['packet_stats']:
            

        # if 'throughput_list' in row[0]:
        #     for data_point in row[1:]:
        #         data_to_plot.append(float(data_point))
        #     ax.plot(data_to_plot, label=row[0])

graphs_to_plot = []

plt.legend(loc='upper right')

plt.show()