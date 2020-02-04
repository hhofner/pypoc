import network
import topology

import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import networkx as nx
import numpy as np

import pickle

sns.set()
sns.set_style('whitegrid')
sns.set_context('poster')
# fig, (ax1, ax2, ax3) = plt.subplots(3,1)
palette = itertools.cycle(sns.color_palette())

###### Plot a "Complex SAGIN Network" ######
# plt.yticks([])
# plt.xticks([])
# net = network.run_network(5, structure=topology.sagin, src_node_count=10)
# nx.draw_networkx(net)

# simple_network = None
throughputs = []
packet_loss_rates = []
packet_avg_delays = []

src_node_count = np.arange(4, 40)
for count in src_node_count:
    net = network.run_network(5, structure=topology.linear, bandwidth=1e3, src_node_count=count)
    packet_loss_rates.append(net.packet_drop_rate)
    throughputs.append(net.overall_throughput/1e3)

    packet_delays = []
    for node in net.nodes:
        if node.type == 2:
            for packet in node.queue:
                packet_delays.append(packet.delay)
    packet_avg_delays.append(sum(packet_delays)/len(packet_delays) * net.step_value)

# pickle_out = open('throughputs_1e3', 'wb')
# pickle.dump(throughputs, pickle_out)
# pickle_out.close()

# pickle_out = open('p_loss_rate_data_1e3', 'wb')
# pickle.dump(packet_loss_rates, pickle_out)
# pickle_out.close()

# pickle_out = open('p_avg_delay_data_1e3', 'wb')
# pickle.dump(packet_avg_delays, pickle_out)
# pickle_out.close()

plt.plot(src_node_count, throughputs)

''' Throughput plot '''
# t1 = pickle.load(open("throughputs_1e3", "rb" ))
# t2 = pickle.load(open("throughputs_2e3", "rb" ))

# plt.plot(t1, color='blue', label='8Kbps', marker='o')
# plt.plot(t2, color='green', label='16Kbps', marker='*')
# plt.legend()

# plt.title("Throughput Results for Increasing Source Nodes")
# plt.xlabel("Number of Source Nodes")
# plt.ylabel("Kbps")

''' Packet Loss Rate Plot'''
# pl1 = pickle.load(open("p_loss_rate_data_1e3", "rb" ))
# pl2 = pickle.load(open("p_loss_rate_data_2e3", "rb" ))

# plt.plot(pl1, color='blue', label='8Kbps', marker='o')
# plt.plot(pl2, color='green', label='16Kbps', marker='*')
# plt.legend()

# plt.title("Packet Loss Rate for Increasing Source Nodes")
# plt.xlabel("Number of Source Nodes")
# plt.ylabel("Percent (%)")

''' Packet Average Delay '''
# d1 = pickle.load(open("p_avg_delay_data_1e3", "rb" ))
# d2 = pickle.load(open("p_avg_delay_data_2e3", "rb" ))

# plt.plot(d1, color='blue', label='8Kbps', marker='o')
# plt.plot(d2, color='green', label='16Kbps', marker='*')
# plt.legend()

# plt.title("Average Packet Delay for Increasing Source Nodes")
# plt.xlabel("Number of Source Nodes")
# plt.ylabel("Seconds")

plt.show()