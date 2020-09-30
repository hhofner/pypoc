import argparse
import logging

import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_queue(filepaths):
    for filepath in filepaths:
        queues = []
        with open(filepath, 'r') as f:
            for line in f.readlines():
                if 'queue_size' in line and 'rel' in line:
                    LOGGER.debug('Reading queue size line')
                    queue = line.split(',')[1:]
                    queue = [float(n)*1000000 for n in queue]

            queues.append(queue)
        queue_df = pd.DataFrame(queues)
        averages = queue_df.mean().tolist()
        if filepath == 'set_one_data/OSPF.csv':
            label = 'OSPF'
            color = 'darkgrey'
        elif filepath == 'set_one_data/Q-Offloading.csv':
            label = 'OSPF w/ Q-Offloading'
            color = 'black'
        else:
            label = filepath
            color = 'blue'
        plt.plot(averages, label=label, color=color)

    plt.legend()
    plt.title('Average amount of data in queue per time')
    plt.xlabel('Time')
    plt.ylabel('Bytes')
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', nargs='*')
    args = parser.parse_args()

    plot_queue(args.files)
