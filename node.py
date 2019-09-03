import simpy
import logging

logging.basicConfig(filename="node.log", level=logging.INFO, filemode="w")

class Node:
    current_id = 0
    @staticmethod
    def get_id():
        id = Node.current_id
        Node.current_id += 1
        return id

    def __init__(self, env):
        self.id = Node.get_id()
        self.env = env
        try:
            self.action = env.process(self.run())
        except ValueError as err:
            print(f"Node {self.id}\'s run() method must be overwritten!\nError message: {err}")

        logging.info(f"Instantiating Node {self.id}")
        self.x = None
        self.y = None
        self.z = None

    def run(self):
        pass


if __name__ == "__main__":
    pass
    # env = simpy.Environment()
    # node = Node(env)
    # env.run(until=10)
