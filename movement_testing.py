import network
import node

minutes = 5
bandwidth = 1e3
packet_size = 500

# Mobility Model
def linear_movement(network, time_step, position):
    x, y, z = position
    return (x+1, y, z)

# Build network topology
src_node = node.VaryingTransmitNode(0, 1, linear_movement, 500, 125)
dest_node = node.MovingNode(2, 1, None)
links = [(src_node, dest_node, {'Bandwidth': bandwidth, 'Channel': 0})]

# Initialize network
network = network.PyPocNetwork()
network.add_edges_from(links)

network.initialize(packet_size=packet_size)
network.run_for(minutes)

for node in network.nodes:
    print(node.mobility_model)
    if node.is_moving:
        print(node.data['position_list'])