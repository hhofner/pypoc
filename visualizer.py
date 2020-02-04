'''
'''
import itertools

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

__author__ = 'Hans Hofner'

class Visualizer:
    def __init__(self, figure_shape):
        sns.set()
        sns.set_style('whitegrid')
        sns.set_context('poster')
        self.current_axes = None
        self.fig, self.axes = plt.subplots(figure_shape[0], figure_shape[1])
        self.axes = np.array(self.axes).flatten()
        self.palette = itertools.cycle(sns.color_palette())

    def next_axes(self):
        if self.current_axes is None:
            self.current_axes = 0
            return (True, self.axes[self.current_axes])
        else:
            self.current_axes += 1
            if self.current_axes >= len(self.axes):
                return (False, None)
            else:
                return (True, self.axes[self.current_axes])

    def draw_throughput(network):
        pass

if __name__ == '__main__':
    visualize = Visualizer((2, 2))
    # print(visualize.next_axes())