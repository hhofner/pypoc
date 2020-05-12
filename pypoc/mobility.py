''' Defines mobility models (generator methods)
'''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize

from enum import Enum
from collections import namedtuple
from copy import deepcopy
import math

WALKING_SPEED = 1.4 #m/s
def distance(position1, position2):
    distance =  np.linalg.norm(np.array(position1)-np.array(position2))
    return distance

class MobilityEnum:
    class WalkingWaypointMovement:
        def __init__(self, network, node):
            '''
            Modeling a random waypoint movement. Randomly pick a position
            within the area of simulation and a velocity, and move there
            and then wait, then do it again.
            :param network: networkx object
            :param node: node object reference
            '''
            self.target_position = None
            self.network = network
            self.node = node
            self.current_tick = 0
            self.speed = WALKING_SPEED * self.network.step_value
            self.direction = self.get_new_direction()

        def get_new_direction(self):
            #print('Geting new direction')
            position = self.node.position
            target_x, target_y = np.random.normal(size=(2,))
            target_x = min(self.network.meta.area[0], target_x*self.network.meta.area[0]) if target_x > 0 else \
                    max(self.network.meta.area[0], target_x*self.network.meta.area[0])
            target_y = min(self.network.meta.area[1], target_y*self.network.meta.area[1]) if target_y > 0 else \
                    max(self.network.meta.area[1], target_y*self.network.meta.area[1])
            vector_to_target = (target_x - position[0], target_y - position[1])

            #Normalize vector
            normalization_factor = math.sqrt(vector_to_target[0]**2+vector_to_target[1]**2)
            normalized_vector = np.array((vector_to_target[0]/normalization_factor, vector_to_target[1]/normalization_factor, 0))

            self.target_position = np.array((target_x, target_y, 0))
            return normalized_vector

        def get_next_position(self):
            #print(f'Target destination: {self.target_position}')
            elapsed_ticks = self.network.tick - self.current_tick
            if elapsed_ticks < 0:
                raise Exception('Elapsed tick problem')
            to_move_distance = np.array(self.direction * elapsed_ticks * self.speed)
            self.current_tick = self.network.tick

            if distance(self.node.position, self.target_position) < distance(
                                                                        np.array(self.node.position)+\
                                                                                self.direction*self.speed,
                                                                        self.target_position):
                self.direction = self.get_new_direction()

            return np.array(self.node.position) + to_move_distance

    #TODO: Change to generator
    def random_movement(network, time_step, position):
        speed = 2 # meters per second
        speed_per_tick = speed * network.step_value * network.tick
        old_x, old_y, old_z = position
        while True:
            yield (old_x + speed_per_tick* np.random.normal(),
                   old_y + speed_per_tick* np.random.normal(),
                   old_z)

    def linear_line_x(network, time_step, position):
        speed = 5 # meters per second
        speed_per_tick = speed * network.step_value
        old_x, old_y, old_z = position
        return (old_x + speed_per_tick, old_y, old_z)

    def get_movement(key):
        mobility_methods = {'LINEAR_X': MobilityEnum.linear_line_x,
                            'RANDOM': MobilityEnum.random_movement,
                            'WALKING_WAYPOINT': MobilityEnum.WalkingWaypointMovement}
        if key not in mobility_methods:
            print(f'key: `{key}` not found in list of available method keys: {mobility_methods}')
            return None
        else:
            return mobility_methods[key]

    def ellipse_movement(network, time_step, position):
        x = []; y = []
        t = np.arange(0, 2*np.pi, 0.01)
        for p in t:
            x.append(10*math.cos(p)); y.append(2*math.sin(p))
        ind = x.index((position[0]))
        return (x[(ind+1) % len(x)], y[(ind+1) % len(y)], position[2]) # modulus to loop around


if __name__ == '__main__':
   print('Herein lies an empty implementation.')
