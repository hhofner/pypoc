import node

class Network:
    def __init__(self):
        self.nodes      = []
        self.outerNodes = []
        self.UAVs       = [] #todo is this a good design?
        self.cloudlets  = []
        self.users      = []
        self.venues     = []

        self.cloud
        # priority_queue<Node*, vector<Node*>, Compare> m_priNodes;
        # priority_queue<Node*, vector<Node*>, CompareRandom> m_priNodesRandom;
        # Graph * m_conGraph; // graph of channel assignment
        # DGraph * m_dGraph; // graph of routing
        # property_map < Graph, vertex_index_t >::type
        # node_index = get(vertex_index, *m_conGraph);
        # property_map < Graph, edge_index_t >::type
        # edges_index = get(edge_index, *m_conGraph);
        # property_map < DGraph, edge_index_t >::type
        # edges_index_d = get(edge_index, *m_dGraph);
        # property_map < Graph, edge_weight_t >::type
        # edges_weight_channel = get(edge_weight, *m_conGraph);
        # property_map < DGraph, edge_weight_t >::type
        # edges_weight_load = get(edge_weight, *m_dGraph);

        self.inData
        self.inDataSize
        self.cuTime

