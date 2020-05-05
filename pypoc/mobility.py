''' Defines mobility models (generator methods)
'''
import numpy as np

from enum import Enum
import math

class MobilityEnum(Enum):
    def random_movement(network, time_step, position):
        speed = 5 # meters per second
        speed_per_tick = speed * network.step_value
        old_x, old_y, old_z = position
        return (old_x + speed_per_tick* np.random.normal(),
                old_y + speed_per_tick* np.random.normal(),
                old_z)

    def linear_line_x(network, time_step, position):
        speed = 5 # meters per second
        speed_per_tick = speed * network.step_value
        old_x, old_y, old_z = position
        return (old_x + speed_per_tick, old_y, old_z)

    def get_movement(key):
        mobility_methods = {'LINEAR_X': MobilityEnum.linear_line_x,
                            'RANDOM': MobilityEnum.random_movement}
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
    print('No implementation!')