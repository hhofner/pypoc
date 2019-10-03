import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from archive import simple_network
import networkx as nx

from archive.topology_schemes import test_topology

time_step_value = 0.001
net_time = 1000
network = simple_network.Network(net_time, time_step_value)
network._bandwidth = 10000000 #10 MHz
network._sinr = 2
network.set_up_network_with(test_topology)

network.run()
data = pd.DataFrame(network.node_values)
print(data)

sns.set()

def graphs_with_topology():
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

    ###### AX1 ######
    ax1.set_title("Network Overview")
    nx.draw(network.network, with_labels=True, ax=ax1)

    ###### AX2 ######
    ax2.set_title(f'Throughput by Nodes')
    ax2.set_xlabel(f'Nodes')
    ax2.set_ylabel(f'Throughput')


def graphs_without_topology():
    fig, ax = plt.subplots()
    dropped_packets_series = []
    for t in range(net_time):
        total = 0
        for node_id in network.dropped_packets.keys():
            total += network.dropped_packets[node_id][t]
        dropped_packets_series.append(total)

    ax.plot(dropped_packets_series, color="r")
    time = list(network.packet_transmit_count.keys())
    p = list(network.packet_transmit_count.values())
    ax.plot(time, p)
    ax.set_title

if len(network.nodes) > 20:
    graphs_without_topology()
else:
    graphs_with_topology()

###### AX2 ######
# data[9].plot(ax=ax2)
# ax2.set_title("Edge Weights = Packets Transmitted Through Edge")
# ax2.set_xlabel("Time")
# ax2.set_ylabel("Num of Packets in Queue")
# plt.show()
