import itertools
import random
from node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode

# TODO: change to allow any connection between number of relays
def grid(src_count=4, relay_count=8, dest_count=4):
    src_nodes = [VaryingTransmitNode(0, 1, None, 500, 125) for _ in range(src_count)]
    relay_nodes_src_side = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(int(relay_count/2))]
    relay_nodes_dest_side = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(int(relay_count/2))]
    dest_nodes = [MovingNode(2, 1, None) for _ in range(dest_count)]

    c1 = []; c2 = []
    src_relay = (n for n in itertools.cycle(relay_nodes_src_side))
    for src in src_nodes:
        c1.append((src, next(src_relay),
                {'Bandwidth': 1e3, 'Channel': 0}))
    for i in range(4):
        c2.append((relay_nodes_dest_side[i], dest_nodes[i], 
            {'Bandwidth': 1e3, 'Channel': 0}))

    # c3 = [(rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0})
    #     for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_src_side]
    
    # direct src_side to dest_side AND between src connections
    c3 = []
    for i in range(len(relay_nodes_src_side)):
        rel1 = relay_nodes_src_side[i]
        rel2 = relay_nodes_dest_side[i]
        c3.append((rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0}))

    # Connections between all src nodes
    c3.extend([(rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0})
                for rel1 in relay_nodes_src_side for rel2 in relay_nodes_src_side])

    c3.extend([(rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0})
                for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_dest_side])

    return c1 + c2 + c3

def sagin(src_count=4, uav_count=4, sat_count=2, dest_count=4, bandwidth=1e3):
    src_nodes = [VaryingTransmitNode(0, 1, None, 500, 125) for _ in range(src_count)]
    uav_src_side = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(uav_count)]
    sat_nodes = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(sat_count)]
    uav_dest_side = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(uav_count)]
    dest_nodes = [MovingNode(2, 1, None) for _ in range(dest_count)]

    # Src to UAV
    c1 = [(src, rel, {'Bandwidth': bandwidth, 'Channel': 0})
          for rel in uav_src_side for src in src_nodes]

    # UAV to Dest
    c2 = [(rel, dest, {'Bandwidth': bandwidth, 'Channel': 0})
          for rel in uav_dest_side for dest in dest_nodes]

    # UAV to UAV
    c3 = [(rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0})
        for rel1 in uav_src_side for rel2 in uav_dest_side]

    # Src-UAV to Sat
    c4 = [(rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0})
        for rel1 in uav_src_side for rel2 in sat_nodes[0:1]]

    # Dest-UAV to SAT
    c5 = [(rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0})
        for rel1 in uav_dest_side for rel2 in sat_nodes[1:]]

    # sat to sat
    c6 = [(rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0})
        for rel1 in sat_nodes for rel2 in sat_nodes]

    return c1 + c2 + c3 + c4 + c5 + c6

###################################################################################################
# Drawing Helper Methods #
def get_sagin_positional(network):
    pos_dict = {}
    whatever = [(1,0), (2,0), (3,0), (4,0), (1,1), (2,1), (3,1), (4,1), (3, 2), (6, 2), (5, 1), (6, 1), (7, 1), (8, 1), (5, 0), (6, 0), (7, 0), (8, 0)]
    for node in network:
        print(node.id)
        pos_dict[node] = whatever[node.id]
    
    return pos_dict