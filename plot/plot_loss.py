import argparse
import logging

import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def plot_file(filepaths):
    for filepath in filepaths:
        with open(filepath, 'r') as f:
            loss = []
            for line in f.readlines():
                print(line.split(',')[0])
                if '_loss' in line:
                    if 'node_168' in line:
                        continue
                    LOGGER.debug('Reading loss line')
                    l = line.split(',')[1:]
                    l = [float(n) for n in l]

                    l.reverse()
                    l_true = l[:400]
                    print(l)
                    filtered = [i for i in l[400:] if i < 1.7]
                    l_true.extend(filtered)
                    loss.append(l_true)

                    plt.plot(l_true, label=line.split(',')[0])

    plt.legend()
    plt.title('Loss per training epochs')
    plt.xlabel('Training epoch')
    plt.ylabel('Loss')
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', nargs='*')
    args = parser.parse_args()

    plot_file(args.files)
