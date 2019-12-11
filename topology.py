import itertools
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

    c3 = [(rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0})
        for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_src_side]

    return c1 + c2 + c3

def sagin():
    src_nodes = [VaryingTransmitNode(0, 1, None, 500, 125) for _ in range(4)]
    relay_nodes_src_side = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(4)]
    relay_nodes_dest_side = [VaryingRelayNode(1, 1, None, 500, 625) for _ in range(4)]
    dest_nodes = [MovingNode(2, 1, None), MovingNode(2, 1, None), MovingNode(2, 1, None), MovingNode(2, 1, None)]

    # c1 = [(src, rel, {'Bandwidth': 1e3, 'Channel': 0})
    #       for rel in relay_nodes_src_side for src in src_nodes]

    # c2 = [(rel, dest, {'Bandwidth': 1e3, 'Channel': 0})
    #       for rel in relay_nodes_dest_side for dest in dest_nodes]

    c3 = [(rel1, rel2, {'Bandwidth': 1e3, 'Channel': 0})
        for rel1 in relay_nodes_dest_side for rel2 in relay_nodes_src_side]

    return c1 + c2 + c3

###################################################################################################

