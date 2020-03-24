'''
Main entry script for PyPoc. Reads the config and 
creates & runs a Network.
'''
import network
import toml

__author__ = 'Hans Hofner'

configuration = toml.load('config.toml')

new = network.PyPocNetwork()
new.run_network_with(configuration)