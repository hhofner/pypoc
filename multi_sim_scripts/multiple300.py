import pypoc
import toml
import os
import time
import argparse
import shutil
import time

NUMBER_OF_SOURCE_NODES = list(range(300, 400))
SIMULATION_RUN_NAME = 'BASELINE'

error_files = []

config_files = []
print(f'{"$"*30} Creating Config Files {"$"*30}')
time.sleep(3)
for num_src_nodes in NUMBER_OF_SOURCE_NODES:
    # Copy file
    new_config_name = f'config_{num_src_nodes}.toml'
    if os.path.isfile(new_config_name):
        continue
    shutil.copyfile('config.toml', new_config_name)
    print(f'Creating copy of config: {new_config_name}')
    new_config = toml.load(new_config_name)
    new_config['nodes']['src-nodes']['count'] = num_src_nodes
    new_config['nodes']['dest-nodes']['count'] = int(num_src_nodes/3)
    new_config['title'] = SIMULATION_RUN_NAME + f'_{num_src_nodes}'

    # Save it back to file
    f = open(new_config_name, mode='w')
    toml.dump(new_config, f)
    f.close()
    config_files.append(new_config_name)

for config_file in config_files:
    print(f'{"$"*30} Running Simulation with {config_file} {"$"*30}')
    try:
        os.system(f"python pypoc --run --config {config_file}")
    except:
        print('Couldnt run for config {config_file}')
        error_files.append(config_file)
    else:
        print('Done! Removing {config_file}')
        os.remove(config_file)

print('Files we werent able to run:')
print(error_files)
