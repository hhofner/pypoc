import network
import node

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
import itertools
import signal_tools
import pickle

minutes = 10
bandwidth = 1e3
packet_size = 500

# Mobility Model
def linear_movement(network, time_step, position):
    x, y, z = position
    return (x+1, y, z)

def ellipse_movement(network, time_step, position):
    x = []; y = []
    t = np.arange(0, 2*np.pi, 0.01)
    for p in t:
        x.append(10*math.cos(p)); y.append(2*math.sin(p))
    ind = x.index((position[0]))
    return (x[(ind+1) % len(x)], y[(ind+1) % len(y)], position[2]) # modulus to loop around

def random_movement(network, time_step, position):
    x, y, z = position
    if network.tick % 25: 
        if x > 3:
            x = x - max(np.random.normal(4, 2), 0.4)
        else:
            x = x + max(np.random.normal(1), 0.4)
        if y > 3:
            y = y - max(np.random.normal(4, 2), 0.4)
        else:
            y = y + max(np.random.normal(1), 0.4)
    
    return (x, y, z)


# Build network topology
src_node1 = node.VaryingTransmitNode(0, 1, ellipse_movement, 500, 125)
# src_node2 = node.VaryingTransmitNode(0, 1, ellipse_movement, 500, 125)
src_node1.position = (1.0, 0, 0)
# src_node2.position = (5.0, 0, 0)

dest_node = node.MovingNode(2, 1, None)
links = [(src_node1, dest_node, {'Bandwidth': bandwidth, 'Channel': 0})]
# links.append((src_node2, dest_node, {'Bandwidth': bandwidth, 'Channel': 0}))

# Initialize network
network = network.PyPocNetwork()
network.add_edges_from(links)

network.initialize(packet_size=packet_size)
network.run_for(minutes)

# for node in network.nodes:
#     print(node.mobility_model)
#     if node.is_moving:
#         print(node.data['position_list'])

x = []; y = []
t = np.arange(0, 2*np.pi, 0.01)
for p in t:
    x.append(10*math.cos(p)); y.append(2*math.sin(p))
# for p in src_node1.data['position_list']:
#     x.append(p[0]); y.append(p[1])

# pickle_out = open('moving_8_23_14_pdf', 'wb')  # wave-frequency, bandwidth, transmit power
# pickle.dump(network.data['throughputs'], pickle_out)
# pickle_out.close()
# d1 = pickle.load(open("moving_15_25_12_pdf", "rb" ))
# d2 = pickle.load(open("moving_16_43_16_pdf", "rb" ))
# d3 = pickle.load(open("moving_45_65_12_pdf", "rb" ))
sns.set()
sns.set_style('whitegrid')
palette = itertools.cycle(sns.color_palette())

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.plot(network.data['throughputs'][2:], color=next(palette), label="moving_16_43_24")
# ax1.plot(d1, color=next(palette), label="moving_15_25_12")
# ax1.plot(d2, color=next(palette), label="moving_16_43_16")
# ax1.plot(d3, color=next(palette), label="moving_45_65_12")
ax1.legend()
ax1.set_title(f'Instantaneous Bandwidths for Moving Node')
ax1.set_ylabel('bps')
ax1.set_xlabel('time (s)')
ax2.scatter(x, y, color='blue', label='Source Node Path')
ax2.scatter(0, 0, color='green', label='Destination Node')
ax2.legend()
ax2.set_xlim(-10, 10)
ax2.set_ylim(-10, 10)
ax2.set_title('2Dimensional 2-Node Topology in Meters')
plt.show()