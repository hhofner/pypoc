import os
import argparse
import logging
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_avg_delay(filedirectory):
    def get_num(x):
        np = x.split('_')[-1]
        return(int(np[:np.index('.')]))

    batch_sets = defaultdict(list)

    for filename in os.listdir(filedirectory):
        if filename[-3:] == 'csv':
            batch_name = filename[:filename.index('_')]
            batch_sets[batch_name].append(os.path.join(filedirectory, filename))
    input(batch_sets)

    for batch_key in batch_sets:
        delays = []
        x_numbers = []
        for filepath in sorted(batch_sets[batch_key], key=get_num):
            delay = []
            step_value = None
            with open(filepath, 'r') as f:
                current_packet = None
                born_tick = None
                died_tick = None
                for line in f.readlines():
                    if step_value is None:
                        if 'step_value' in line:
                            step_value = float(line.split(',')[1])

                    if 'packet' in line and 'path' in line and 'dest-nodes' in line:
                        current_packet = int(line.split(',')[0].split('_')[1])
                        LOGGER.debug(f'Current packet: {current_packet}')
                        continue
                    if current_packet:
                        if f'packet_{current_packet}' in line and 'born_tick' in line:
                            born_tick = int(line.split(',')[1])
                            LOGGER.debug(f'Reading born tick: {born_tick}')

                        if f'packet_{current_packet}' in line and 'died_tick' in line:
                            died_tick = int(line.split(',')[1])

                            LOGGER.debug(f'Reading died tick: {died_tick}')
                            delay.append(died_tick - born_tick)
                            current_packet = None
                            born_tick = None
                            died_tick = None

            delays.append(step_value*(sum(delay)/len(delay)*30))
            x_numbers.append(get_num(filepath))
        input(batch_key)
        if 'BASELINE' in batch_key:
            label = 'OSPF'
            x_numbers = np.array(x_numbers) - 1
        else:
            label = 'OSPF Q-Offloading'
            x_numbers = np.array(x_numbers) + 1
        plt.bar(x_numbers, delays, 2, label=label)

    plt.title('Average packet delay in milliseconds')
    plt.ylabel('ms')
    plt.xlabel('Source node count')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--files')
    args = parser.parse_args()

    plot_avg_delay(args.files)
