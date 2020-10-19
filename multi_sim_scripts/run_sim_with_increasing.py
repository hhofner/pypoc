''' Script needs to be run from 
root dir PyPoc/ (not PyPoc/multi_sim_scripts)
'''
import toml
import os
import time
import argparse
import shutil
import time

import numpy as np

class MultiSim:
    def __init__(self, config, var, starting, ending, steps, data_directory, sim_name):
        try:
            test_config_loading = toml.load(config)
        except:
            raise Exception (f"Problem TOML loading {config}")

        self.config = config

        self.var = var
        self.cs = str(var).split('.')  # expected: ['src-nodes', 'count']
        self.len_config = len(self.cs) # expected (for above): 2
        self.c_var = None # <-- reference to dict

        self.starting_point = int(starting)
        self.ending_point = int(ending)
        self.steps = int(steps)

        self.SIMULATION_RUN_NAME = sim_name
        self.data_dir = data_directory
        if not os.path.isdir(data_directory):
            raise Exception(f'{data_directory} not a dir')

    def run(self):
        # Create a list values that the config var should change to
        config_variable_values = np.arange(self.starting_point, self.ending_point, self.steps)

        error_files = []
        config_files = []

        # Create new config file for every value
        print(f'{"$"*30} Creating Config Files {"$"*30}')
        for temp_var_value in config_variable_values:

            new_config_name = self.data_dir + '/' + self.SIMULATION_RUN_NAME + f'{self.var}_{temp_var_value}.toml'
            # If the file exist, no need to create it, so skip(continue)
            if os.path.isfile(new_config_name):
                continue
            # If it doesn't exist, make a copy to the specified data directory
            shutil.copyfile(f'{self.config}', new_config_name)
            print(f'Creating copy of config: {new_config_name}')
            # Check if key exists and get reference to variable that needs to change
            new_config = toml.load(new_config_name)
            # c_var <- reference to dict containing key to change
            # self.cs <- list of specified keys incase of nested keys
            try:
                if self.len_config == 4:
                    new_config[self.cs[0]][self.cs[1]][self.cs[2]][self.cs[3]]
                    c_var = new_config[self.cs[0]][self.cs[1]][self.cs[2]]
                elif self.len_config == 3:
                    new_config[self.cs[0]][self.cs[1]][self.cs[2]]
                    c_var = new_config[self.cs[0]][self.cs[1]]
                elif self.len_config == 2:
                    new_config[self.cs[0]][self.cs[1]]
                    c_var = new_config[self.cs[0]]
                elif self.len_config == 1:
                    new_config[self.cs[0]]
                    c_var = new_config
            except KeyError:
                print(f"Error finding key {self.cs}")
                raise   # Copy file

            c_var[self.cs[-1]] = int(temp_var_value) # c_var is reference to dict, self.cs[-1] is the key to the val we want
            new_config['title'] = self.SIMULATION_RUN_NAME + f'_{self.var}_{temp_var_value}'

            # Save it back to file
            f = open(new_config_name, mode='w')
            toml.dump(new_config, f)
            f.close()
            config_files.append(new_config_name) # new_config_name is full path

        input(f'Here are the config files to run: {config_files}')
        for config_file in config_files:
            print(f'{"$"*30} Running Simulation with {config_file} {"$"*30}')
            try:
                os.system(f"python -m pypoc --run --config {config_file} --output_dir {self.data_dir}")
            except:
                print('Couldnt run for config {config_file}')
                error_files.append(config_file)
            except KeyboardInterrupt:
                print('Detected keyboard interrupt, quitting')
                break
            else:
                print(f'Done! Removing {config_file}')
                os.remove(config_file)

        print('Files we werent able to run:')
        print(error_files)
