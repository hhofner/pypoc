import itertools
import random
import argparse
import numpy as np
from pypoc.node import Packet, Node, VaryingTransmitNode, VaryingRelayNode, MovingNode, RestrictedNode
from pypoc.mobility import ellipse_movement, straight_line

# TODO: change to allow any connection between number of relays
def grid(src_count=4, relay_count=8, dest_count=4, bandwidth=1e3):
    src_nodes = [VaryingTransmitNode(0, 1, None, 500, 125) for _ in range(src_count)]
    relay_nodes_src_side = [RestrictedNode(1, 1, None, 500, 625, 20e3) for _ in range(int(relay_count/2))]
    relay_nodes_dest_side = [RestrictedNode(1, 1, None, 500, 625, 20e3) for _ in range(int(relay_count/2))]
    dest_nodes = [MovingNode(2, 1, None) for _ in range(dest_count)]

    c1 = []; c2 = []
    src_relay = itertools.cycle(relay_nodes_src_side)
    for src in src_nodes:
        c1.append((src, next(src_relay),
                {'Bandwidth': bandwidth, 'Channel': 0}))
    for i in range(4):
        c2.append((relay_nodes_dest_side[i], dest_nodes[i], 
            {'Bandwidth': bandwidth, 'Channel': 0}))

    # c3 = [(rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0})
    #     for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_src_side]
    
    # direct src_side to dest_side AND between src connections
    c3 = []
    for i in range(len(relay_nodes_src_side)):
        rel1 = relay_nodes_src_side[i]
        rel2 = relay_nodes_dest_side[i]
        c3.append((rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0}))

    # Connections between all src nodes
    c3.extend([(rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0})
                for rel1 in relay_nodes_src_side for rel2 in relay_nodes_src_side])

    c3.extend([(rel1, rel2, {'Bandwidth': bandwidth, 'Channel': 0})
                for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_dest_side])

    return c1 + c2 + c3

def sagin(src_count=4, uav_count=4, sat_count=2, dest_count=4, bandwidth=1e3):


    src_nodes = [VaryingTransmitNode(0, 1, None, 500, 500) for _ in range(src_count)]
    uav_src_side = [RestrictedNode(1, 1, None, 500, 625, 3e3) for _ in range(uav_count)]
    sat_nodes = [RestrictedNode(1, 1, None, 500, 625, 6e3) for _ in range(sat_count)]
    uav_dest_side = [RestrictedNode(1, 1, None, 500, 625, 3e3) for _ in range(uav_count)]
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
    c6 = [(rel1, rel2, {'Bandwidth': 2 * bandwidth, 'Channel': 0})
        for rel1 in sat_nodes for rel2 in sat_nodes]

    return c1 + c2 + c3 + c4 + c5 + c6

def linear(src_count= 2, uav_count=0, sat_count=0, dest_node_count=0, bandwidth=1e3):
    '''
    Create a "linear" topology for testing purposes. Default is
    source and destination node.
    '''
    if src_count == 2:
        src_node = VaryingTransmitNode(type=0, 
                                       step_value=1, 
                                       mobility_model=straight_line, 
                                       packet_size=500, 
                                       gen_rate=1000)
        src_node.position = (-1.0, 0, 0)
        dest_node = MovingNode(2, 1, None)
        return [(src_node, dest_node, {'Bandwidth': bandwidth, 'Channel': 0})]
    if src_count == 3:
        pass

###################################################################################################
# Positional Topologies #
def normal_distributed(bs_count):
    pass

def sagin0115topology():
    '''
    Return list of edge tuples for topology.
    '''
    # Global Parameters
    width = 10
    height = 10
    packet_size = 500  #Bytes == 4Kbits

    # Satellite Parameters
    satellite_cluster_count = 2
    satellite_cluster_size = 1
    sat_buffer_size = 30000  # 30MB
    sat_z = 2000e3 # 2000 Kilometers

    satellite_nodes = []
    # Build Satellites Nodes
    for cluster in range(satellite_cluster_count):
        for count in range(satellite_cluster_size):
            node = RestrictedNode(type=1, step_value=1,
                                    mobility_model=None,
                                    packet_size=packet_size,
                                    gen_rate=0,
                                    max_buffer_size=sat_buffer_size)
            x = np.random.random(1)[0] * width/2
            y = np.random.random(1)[0] * height/2
            z = sat_z
            node.position = (x, y, z)
            satellite_nodes.append(node)
        
    # UAV-BS Parameters
    

        

###################################################################################################
# Drawing Helper Methods #
def get_sagin_positional(network):
    pos_dict = {}
    whatever = [(1,0), (2,0), (3,0), (4,0), (1,1), (2,1), (3,1), (4,1), (3, 2), (6, 2), (5, 1), (6, 1), (7, 1), (8, 1), (5, 0), (6, 0), (7, 0), (8, 0)]
    for node in network:
        print(node.id)
        pos_dict[node] = whatever[node.id]
    
    return pos_dict

if __name__ == '__main__':
    print(f'>> Plotting top-down topology map:')
    