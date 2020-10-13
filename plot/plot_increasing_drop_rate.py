import argparse
import logging
import os
from collections import defaultdict

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_file(filedirectory):
    def get_num(x):
        np = x.split('_')[-1]
        return(int(np[:np.index('.')]))

    batch_sets = defaultdict(list)

    for filename in os.listdir(filedirectory):
        if filename[-3:] == 'csv':
            batch_name = filename[:filename.index('_')]
            batch_sets[batch_name].append(os.path.join(filedirectory, filename))

    for batch_key in batch_sets:
        drop_movement = []
        x_numbers = []
        for filepath in sorted(batch_sets[batch_key], key=get_num):
            with open(filepath, 'r') as f:
                for line in f.readlines():
                    if 'drop_rate_value' in line:
                        value = (1/float(line.split(',')[1]))*100
                        drop_movement.append(value)
                        break
            x_numbers.append(get_num(filepath))
        if batch_key == 'BASELINE':
            color = 'darkgrey'
            label = 'OSPF'
        elif batch_key == 'Q-OFFLOADING':
            color = 'black'
            label = 'OSPF Q-Offloading'
        else:
            color = 'blue'
            label = f'{batch_key}'
        plt.plot(x_numbers, drop_movement, label=label, color=color, linestyle='--')

    plt.legend()
    plt.title('Drop Rate: increasing users')
    #plt.ylim([0.4e8, 1.6e8])
    plt.xlim([80,240])
    plt.xlabel('Source Nodes (Users)')
    plt.ylabel('bit-per-second')
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--files')
    args = parser.parse_args()

    plot_file(args.files)
