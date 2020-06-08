'''
This file will define the environment in abstract parameters such as 
tick time.
'''

class Default:
    def __init__(self, network):
        self.tic
        self.network = network

    def run(self):
        self.network.run()
