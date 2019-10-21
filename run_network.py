import network
'''  DRAW THE NETWORK  '''
# net_data = run_network_for(4, 6, 2, 50, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# print('Arrived Packets:', str(net_data['arrived_count']))
sns.set()
data = [[],[]]
g=4;a=6;s=2
for i in range(1,20):
    g=g+2; a=a+2; s=s+2
    net_data = run_multiple_chan_network_for(g, a, s, 30, 0.001)
    print('Dropped Packets:', str(net_data['dropped_count']))
    dp = net_data['dropped_count']
    print('Arrived Packets:', str(net_data['arrived_count']))
    ap = net_data['arrived_count']
    data[0].append((dp*100)/ap)
    data[1].append(4*i + 6*i + 2*i)
fig, ax = plt.subplots()
ax.plot(data[1],data[0], sns.xkcd_rgb["pale red"])

data = [[],[]]
g=4;a=6;s=2
for i in range(1,20):
    g=g+2; a=a+2; s=s+2
    net_data = run_improved_multiple_chan_network_for(g, a, s, 30, 0.001)
    print('Dropped Packets:', str(net_data['dropped_count']))
    dp = net_data['dropped_count']
    print('Arrived Packets:', str(net_data['arrived_count']))
    ap = net_data['arrived_count']
    data[0].append((dp*100)/ap)
    data[1].append(4*i + 6*i + 2*i)

ax.plot(data[1],data[0], sns.xkcd_rgb["denim blue"])

ax.set_xlabel('Number of nodes')
ax.set_ylabel('Packet loss rate (%)')
ax.legend(['Hardcoded', 'Hardcoded-Optimized'])
# net_data = run_multiple_chan_network_for(4, 6, 2, 300, 0.001)



# print('Dropped Packets:', str(net_data['dropped_count']))
# dp = net_data['dropped_count']
# print('Arrived Packets:', str(net_data['arrived_count']))
# ap = net_data['arrived_count']
# data.append((ap/dp)*100)
#
# net_data = run_multiple_chan_network_for(8, 12, 4, 300, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# dp = net_data['dropped_count']
# print('Arrived Packets:', str(net_data['arrived_count']))
# ap = net_data['arrived_count']
# data.append((ap/dp)*100)
#
# net_data = run_multiple_chan_network_for(16, 24, 8, 300, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# dp = net_data['dropped_count']
# print('Arrived Packets:', str(net_data['arrived_count']))
# ap = net_data['arrived_count']
# data.append((ap/dp)*100)

# net_data = run_network_for(6, 8, 2, 100, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# print('Arrived Packets:', str(net_data['arrived_count']))
# net_data = run_network_for(12, 16, 4, 100, 0.001)
#
# print('Dropped Packets:', str(net_data['dropped_count']))
# print('Arrived Packets:', str(net_data['arrived_count']))

# labels = []
# for key in net_data.keys():
#     if 'lvl' in key:
#         ax.plot(net_data[key][2])
#         labels.append(key)
#     if 'Channel' in key:
#         print(net_data[key]['dropped_packets'])
#
# ax.legend(labels)
# plt.show()
