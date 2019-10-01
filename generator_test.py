import networkx as nx
import generating_node

''' Constants'''
packet_size = 1016 #bits = 127 bytes

network = nx.Graph()

receiving_nodes = []
for _ in range(2):
    new = generating_node.Node(0.001, packet_size=None, queue_size=int(8e8), transmit_rate=None, gen_rate=None)
    receiving_nodes.append(new)

level_one_relays = []
for _ in range(6):
    new = generating_node.Node(0.001, packet_size=None, queue_size=int(600000), transmit_rate=2400, gen_rate=None)
    level_one_relays.append(new)

level_two_relays = []
for _ in range(2):
    new = generating_node.Node(0.001, packet_size=None, queue_size=int(600000), transmit_rate=2400, gen_rate=None)
    level_two_relays.append(new)

transmit_nodes = []
for _ in range(4):
    new_node = generating_node.Node(0.001, packet_size=packet_size, queue_size=int(8e7), transmit_rate=2400, gen_rate=2400)
    transmit_nodes.append(new_node)

'''############### RUN LOOP #################'''
time_steps = 100

print('Starting network...')
while time_steps > 0:

    #### RUNNING NETWORK ####

    #### RUNNING NETWORK ####
    time_steps = time_steps - 1
'''##########################################'''
print('Finished')