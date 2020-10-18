import toml
import os
import time
import argparse
import shutil
import time

import numpy as np

NUMBER_OF_SOURCE_NODES = np.arange(50, 250, 5)
SIMULATION_RUN_NAME = '3_BASELINE_10_17'

error_files = []

config_files = []
print(f'{"$"*30} Creating Config Files {"$"*30}')
for num_src_nodes in NUMBER_OF_SOURCE_NODES:
    # Copy file
    new_config_name = f'3_baseline_{num_src_nodes}.toml'
    if os.path.isfile(new_config_name):
        continue
    shutil.copyfile('output_data/oct_17_groundtruth_3/config.toml', new_config_name)
    print(f'Creating copy of config: {new_config_name}')
    new_config = toml.load(new_config_name)
    new_config['nodes']['src-nodes']['count'] = int(num_src_nodes)
    new_config['title'] = SIMULATION_RUN_NAME + f'_{num_src_nodes}'

    # Save it back to file
    f = open(new_config_name, mode='w')
    toml.dump(new_config, f)
    f.close()
    config_files.append(new_config_name)

for config_file in config_files:
    print(f'{"$"*30} Running Simulation with {config_file} {"$"*30}')
    try:
        os.system(f"python -m pypoc --run --config {config_file}")
    except:
        print('Couldnt run for config {config_file}')
        error_files.append(config_file)
    else:
        print(f'Done! Removing {config_file}')
        os.remove(config_file)

print('Files we werent able to run:')
print(error_files)
