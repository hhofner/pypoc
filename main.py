net_time = 300
network = Network(net_time)
network.set_up_network()
network.run()
data = pd.DataFrame(network.node_values)
print(data)

sns.set()
# fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
fig, ax1 = plt.subplots()

# nx.draw(network.network, with_labels=True, ax=ax1)
# ax1.set_title("Network Overview")

###### AX1 ######
dropped_packets_series = []
for t in range(net_time):
    total = 0
    for node_id in network.dropped_packets.keys():
        total += network.dropped_packets[node_id][t]
    dropped_packets_series.append(total)

ax1.plot(dropped_packets_series, color="r")
time = list(network.packet_transmit_count.keys())
p = list(network.packet_transmit_count.values())
ax1.plot(time, p)

###### AX2 ######
# data[9].plot(ax=ax2)
# ax2.set_title("Edge Weights = Packets Transmitted Through Edge")
# ax2.set_xlabel("Time")
# ax2.set_ylabel("Num of Packets in Queue")
plt.show()
