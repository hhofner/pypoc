import argparse
import logging

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_file(filepaths):
    for filepath in filepaths:
        throughput = []
        with open(filepath, 'r') as f:
            for line in f.readlines():
                if 'throughput_list' in line:
                    LOGGER.debug('Reading throughput line')
                    throughput = line.split(',')[1:]
                    throughput = [float(n) for n in throughput]
                    LOGGER.debug(f'Length of throughpus recorded: {len(throughput)}')
                    break

        if filepath == 'set_one_data/OSPF.csv':
            name = 'OSPF (1)'
            plt.plot(throughput, label=name, color='darkgrey')
        elif filepath == 'set_one_data/Q-Offloading.csv':
            name = 'OSPF w/ Q-Offloading (1)'
            plt.plot(throughput, label=name, color='black')
        elif filepath == 'simulation_data/groundtruth.csv':
            name = 'OSPF (2)'
            plt.plot(throughput, label=name, color='darkgrey', linestyle='--')
        elif filepath == 'simulation_data/q-run.csv':
            name = 'OSPF w/ Q-Offloading (2)'
            plt.plot(throughput, label=name, color='black', linestyle='--')
        else:
            plt.plot(throughput, label=filepath)

    plt.ylim(0.5e8,1.2e8)
    plt.legend()
    plt.title('Throughput per time')
    plt.tick_params(axis='x', which='both', bottom=False)
    plt.xlabel('Time')
    plt.ylabel('bit-per-second')
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', nargs='*')
    args = parser.parse_args()

    plot_file(args.files)
