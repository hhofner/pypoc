import simple_node

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
        tgn.update(**{'generation_rate': int(np.random.normal(100, 50))})

    # update relaying nodes
    for an in air_nodes:
        an.update(**{'serv_rate': 4})
    for sn in sat_nodes:
        sn.update(**{'serv_rate': 2})

    nodes += ground_nodes
    nodes += air_nodes
    nodes += sat_nodes

    return (ebunch, nodes)