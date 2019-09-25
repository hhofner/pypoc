# PYPOC
A Python Discrete Event Simulator for Heterogeneous Wireless Networks

## The Main Players
The main classes of this simulator are the Packet class, the Node class, and 
the Network class, which can be found in packet.py, simple_node.py, and simple_network.py
respectively. 

The general flow and workings is that a Network object will contain a collection of Node objects
and an environment time attribute. Node objects in turn will create, receive and send Packet objects,
which the Network object will handle in between transmissions and receiving (that is, the Network
object somewhat acts as the channel). The Network object iterates over every node and calls "transmit",
collects all packets to be transmitted, evaluates that transmission and then re-iterates through the nodes
and calls the "receive" method if a packet is to be sent to that node. It does this in time steps equal
to the set environment time.

## Setting up a network

#### Creating Nodes for a network
To create a node, first create a dictionary that describes that node
based with the attributes:
- _transmission_rate_
- _gen_scheme_
- _queue_cap_
- _serv_rate_
After creating the topology with the destination nodes, pass the list
of destination node ID's **(IMPORTANT: Not the nodes itself, but the destination
ID's)**

Creating connections is done by creating length of 3 tuples with the form:
(node1.ID, node2.ID, {'attribute': value}) . For now, the 'Weight' attribute
needs to be specified.

#### Important Node Attributes
The following node attributes must be set beforehand.

- _generation_rate_
- _destinations_
- _type_
- _serv_rate_ : Number of packets that are picked off the queue to be transmitted.
- _queue_cap_
- _gen_scheme_
- _logging_file_
- _transmission_rate_ : The rate of transmission per second, ie '10 kb/s' (ten kilobits per second)
 