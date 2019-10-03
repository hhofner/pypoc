import networkx as nx
import generating_node
import simple_channel
import matplotlib.pyplot as plt
import pandas as pd

''' Constants'''
packet_size = 1016 #bits = 127 bytes

network = nx.Graph()
''' Create nodes'''
receiving_nodes = []
for _ in range(2):
    new = generating_node.Node(0.001, packet_size=None, queue_size=int(8e8), transmit_rate=0, gen_rate=0)
    receiving_nodes.append(new)

level_one_relays = []
for _ in range(6):
    new = generating_node.Node(0.001, packet_size=None, queue_size=int(600000), transmit_rate=2400, gen_rate=0)
    level_one_relays.append(new)

level_two_relays = []
for _ in range(2):
    new = generating_node.Node(0.001, packet_size=None, queue_size=int(600000), transmit_rate=2400, gen_rate=0)
    level_two_relays.append(new)

transmit_nodes = []
destination_id_list = [dest.id for dest in receiving_nodes]
for _ in range(4):
    new_node = generating_node.Node(0.001, packet_size=packet_size, queue_size=int(8e7), transmit_rate=2400, gen_rate=2400,
                                    destinations=receiving_nodes)
    transmit_nodes.append(new_node)

''' Create connections '''
channel = simple_channel.Channel(name='test', time_step=0.001, bandwidth=15e6, sinr=1)
ebunch = [] #list of edge-tuples
half1 = len(level_one_relays)//2
for tn in transmit_nodes:
    for rn in level_one_relays[:half1]:
        temp = (tn, rn, {'Weight' : 1, 'Channel': channel})
        ebunch.append(temp)

for dn in receiving_nodes:
    for rn in level_one_relays[half1:]:
        temp = (dn, rn, {'Weight': 1, 'Channel': channel})
        ebunch.append(temp)

for rn1 in level_one_relays:
    for rn2 in level_two_relays:
        temp = (rn1, rn2, {'Weight': 1, 'Channel': channel})
        ebunch.append(temp)

network.add_edges_from(ebunch)

''' Data Structures'''
node_data = {'queue_size': []}
network_data = [dict(node_data) for _ in range(len(network.nodes))]

'''############### RUN LOOP #################'''
time_steps = 10

print('Starting network...')
while time_steps > 0:

    #### RUNNING NETWORK ####
    for node in network.nodes:
        node.generate(network)

        # Transmit through channel
        channel.transmit_access(node.transmit)

    #### RUNNING NETWORK ####
    time_steps = time_steps - 1
'''##########################################'''
print('Finished')

''' DRAW THE NETWORK '''
networkdf = pd.DataFrame(network_data)
print(networkdf)
# fig, ax = plt.subplots()
# nx.draw(network, ax=ax)
# plt.show()