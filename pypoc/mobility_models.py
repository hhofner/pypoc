import numpy as np
import math

def ellipse_movement(network, time_step, position):
    x = []; y = []
    t = np.arange(0, 2*np.pi, 0.01)
    for p in t:
        x.append(10*math.cos(p)); y.append(2*math.sin(p))
    ind = x.index((position[0]))
    return (x[(ind+1) % len(x)], y[(ind+1) % len(y)], position[2]) # modulus to loop around

def straight_line(network, time_step, position):
    old_x, old_y, old_z = position
    return (old_x + 0.1, old_y, old_z)