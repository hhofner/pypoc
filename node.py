import simpy
import logging
from exceptions import RunMethodEmpty

logging.basicConfig(filename="node.log", level=logging.INFO, filemode="w")

class Node(object):
    current_id = 0
    @staticmethod
    def get_id():
        id = Node.current_id
        Node.current_id += 1
        return id

    def __init__(self, **kwargs):
        self.id = Node.get_id()
        logging.info(f"Instantiating Node {self.id}")
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.z = kwargs['z']

        if 'env' in kwargs.keys():
            self.env = kwargs['env']
            try:
                self.action = self.env.process(self.run())
            except ValueError as err:
                raise RunMethodEmpty()

    def add_env(self, env):
        if self.env:
            logging.info("Warning: Overwriting env variable")
            self.env = env
        else:
            self.env = env
            try:
                self.action = self.env.process(self.run())
            except RunMethodEmpty as err:
                raise RunMethodEmpty

    def run(self):
        pass

    def __hash__(self):
        # Returns the hashed representation of the string
        return hash(repr(self))

class MovingNode(Node):
    """ Simple node object with mobility model """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mobility_model = kwargs['mobility_model']

    def run(self):
        #TODO: Error case 
        while True:
            print(f'Node {self.id} at {self.x, self.y, self.z}')
            yield self.env.timeout(1)
            self.x,self.y,self.z = self.mobility_model(self.x, self.y, self.z)

if __name__ == "__main__":
    pass
    # env = simpy.Environment()
    # node = Node(env)
    # env.run(until=10)
