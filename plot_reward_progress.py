import os

import torch
import matplotlib.pyplot as plt

sim_data_file = "simulation_data/none.csv"

memory_set_history = []
with open(sim_data_file, 'r') as sim_data:
    mem_set = None
    for line in sim_data:
        if 'q-stations_memory_set' in line:


