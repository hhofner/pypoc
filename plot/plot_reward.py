import argparse
import logging

import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_file(filepaths):
    for filepath in filepaths:
        with open(filepath, 'r') as f:
            reward = []
            for line in f.readlines():
                if '_memory_set' in line:
                    LOGGER.debug('Reading mem set line')
                    l = line.split(',')[1:]
                    print(l)


    plt.legend()
    plt.title('Loss per training epochs')
    plt.xlabel('Training epoch')
    plt.ylabel('Loss')
#    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', nargs='*')
    args = parser.parse_args()

    p
