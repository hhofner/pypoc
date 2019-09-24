import simple_node
import numpy as np
import channel

def default_sagin(ground_node_count=8, air_node_count=10, space_node_count=4):
    nodes = []
    ebunch = []

    ground_nodes = [simple_node.Node(**{'type': 'ground', 'gen_scheme': 'time_experimental'}) for _ in
                    range(ground_node_count)]
    air_nodes = [simple_node.Node(**{'type': 'air'}) for _ in range(air_node_count)]
    sat_nodes = [simple_node.Node(**{'type': 'space'}) for _ in range(space_node_count)]

    # Transmitting ground nodes to air node connections
    gnc = ground_node_count
    anc = air_node_count
    for gn in ground_nodes[:int(gnc / 2)]:
        gn.update(**{'serv_rate': int(np.random.normal(100, 50))})
        for an in air_nodes[:int(anc / 2)]:
            ebunch.append((gn.id, an.id, {'Weight': 1}))

    # Receiving ground node to air node connections
    for gn in ground_nodes[int(gnc / 2):]:
        for an in air_nodes[int(anc / 2):]:
            ebunch.append((gn.id, an.id, {'Weight': 1}))

    # Air node to air node connections
    for an in air_nodes:
        for an2 in air_nodes:
            if not an is an2:
                ebunch.append((an.id, an2.id, {'Weight': 1}))

    # Air node to space node connections
    for an in air_nodes:
        for sn in sat_nodes:
            ebunch.append((an.id, sn.id, {'Weight': 1}))

    # update transmitting nodes
    destinations = [n.id for n in ground_nodes[int(gnc / 2):]]
    for tgn in ground_nodes[:int(gnc / 2)]:
        tgn.update(**{'destinations': destinations})
        tgn.update(**{'generation_rate': 1})

    # update serve rates
    for an in air_nodes:
        an.update(**{'serv_rate': int(np.random.normal(30, 10))})
    for sn in sat_nodes:
        sn.update(**{'serv_rate': int(np.random.normal(30, 10))})

    nodes += ground_nodes
    nodes += air_nodes
    nodes += sat_nodes

    return (ebunch, nodes)

def test_topology(node_count=2):
    '''
    Test topology building method.
    1. Create nodes
    2. Create their connections in form of ebunches.
    3. Return the ebunch & network

    :param node_count:
    :return:
    '''
    transmit_nodes = []
    receive_nodes  = []

    num_of_transmit = node_count//2
    num_of_receive  = node_count - num_of_transmit

    for _ in range(num_of_receive):
        receive_nodes.append(simple_node.Node())
    for _ in range(num_of_transmit):
        pass
