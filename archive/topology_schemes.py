from archive import simple_node
import numpy as np

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

def test_topology(transmit_node_count=10, relay_node_count=3, receive_node_count=3, time_step_value=3):
    '''
    Test topology building method.
    1. Create nodes
    2. Create their connections in form of ebunches.
    3. Return the ebunch & network

    :param node_count:
    :return:
    '''

    ### Create corresponding configuration dictionaries ###
    tnc = {'transmission_rate': int(40000*time_step_value),
            'queue_cap': 10000000,
            'serv_rate': int(40000*time_step_value),
            'gen_scheme': 'basic_normal',
            }

    rnc = dict(tnc)
    rnc['transmission_rate'] = 0

    dnc = dict(rnc)
    dnc['serv_rate'] = 0

    ### Create Nodes and respective lists ***
    transmit_nodes = [simple_node.Node(**tnc) for _ in range(transmit_node_count)]
    relay_nodes    = [simple_node.Node(**rnc) for _ in range(relay_node_count)]
    receive_nodes  = [simple_node.Node(**dnc) for _ in range(receive_node_count)]

    ### Assign the list of receiving nodes to transmitting nodes ###
    receive_node_IDs = [rcn.id for rcn in receive_nodes]
    for tnode in transmit_nodes:
        tnode.config['destinations'] = receive_node_IDs

    ### Create connections ###
    ebunch = []
    for tnode in transmit_nodes:
        for rnode in relay_nodes:
            ebunch.append((tnode.id, rnode.id, {'Weight': 1}))

    for rnode in relay_nodes:
        for dnode in receive_nodes:
            ebunch.append((rnode.id, dnode.id, {'Weight': 1}))

    nodes = []
    nodes += transmit_nodes
    nodes += relay_nodes
    nodes += receive_nodes

    return (ebunch, nodes)


