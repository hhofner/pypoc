import os
import logging
import config
import time
import math
import random

import pypoc.models as models
import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F
import networkx as nx
from pypoc.node import RestrictedMovingNode

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)

class QNode(RestrictedMovingNode):
    '''
    This node will define all training, recording and updating methods
    for a Q-Network implementation.
    '''
    def __init__(self, node_type, step_value, mobility_model, packet_size, gen_rate, max_buffer_size):
        """ Initialize model training parameters and model itself

        """
        super().__init__(node_type, step_value, mobility_model, max_buffer_size)

        self.TRAINING_RUN = True

        configuration = config.surgeon_model
        capacity = configuration['capacity']  # Capacity for replay memory
        self.max_neighbors = configuration['max_neighbors']  # This defines the input to the DQN, max_neighbors**2

        self.GAMMA = configuration['gamma'] 
        self.BATCH_SIZE = configuration['batch_size'] 

        self.EPS_START = configuration['eps_start'] # Helps the decay in random selection
        self.EPS_END = configuration['eps_end']  # Helps the decay in random selection
        self.EPS_DECAY = configuration['eps_decay']

        self.NETWORK_UPDATE_TICK = configuration['net_tick']

        self.steps_done = 0

        self.action_space = [0, 1]
        self.action_space_size = len(self.action_space)

        self.replay_memory = models.ReplayMemory(capacity)

        # Load up model if available
        if os.path.isfile('./QOFFLOADING'):
            self.policy_net = models.PyTorchQNetwork()
            policy_net_state_dict = torch.load('./QOFFLOADING')
            self.policy_net.load_state_dict(policy_net_state_dict)
        else:
            self.policy_net = models.PyTorchQNetwork()

        self.target_net = models.PyTorchQNetwork()
        # Copy the `state_dict` (weights and bias) from policy to target
        self.target_net.load_state_dict(self.policy_net.state_dict())

        # Sets network into "evaluation mode"
        self.target_net.eval()

        self.optimizer = optim.RMSprop(self.policy_net.parameters())
        LOGGER.debug("Initiated Q-Node!")
        time.sleep(2)

    def initalize_data(self):
        super().initalize_data()
        self.data.update({'memory_set': []})
        self.data.update({'loss':[]})
        self.data.update({'q-values':[]})

    def relay(self, network):
        LOGGER.debug(f'Relaying network from A Q-NODE node: {self}')
        self.state = self.get_state(network)

        epsilon_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
                math.exp(-1 * self.steps_done / self.EPS_DECAY)
        self.steps_done += 1

        self.optimize_model()

        if random.random() > epsilon_threshold:
            LOGGER.debug('Getting action from policy network')
            self.policy_net = self.policy_net.float()
            LOGGER.debug(f'Raw output from policy_net(state): {self.policy_net(self.state.float())}')
            selected_action = self.policy_net(self.state.float()).max(0)[1].view(1, 1)
            self.data['q-values'].append(self.policy_net(self.state.float()).tolist())
            offload = bool(selected_action[0][0])
            LOGGER.debug(f'Selected action from policy net: {"offload" if offload else "dont_offload"}')
        else:
            selected_action = random.choice(self.action_space)
            offload = bool(selected_action)  # if 0, dont offload, if 1, offload

        if self.queue:
            packet = self.queue.pop()

            if not offload:
                packet.next_node.receive(network, packet)
                self.data['relayed_packets'].append(packet)
            else:
                sat_node = network.get_sat_node()
                # Create new path
                try:
                    new_path = random.choice(
                            list(nx.all_shortest_paths(
                                network, sat_node, packet.destination, weight="Channel")))
                except nx.exception.NetworkXNoPath:
                    LOGGER.error(f"No path from sat {sat_node} to dest {packet.destination}")
                    raise
                packet.recal_path(new_path)
                sat_node.receive(network, packet)

            memory_set = {'tick': torch.tensor([network.tick]), 'state': self.state, 
                            'action': torch.tensor([[selected_action]]), 
                            'reward': None, 'next_state': None}
            LOGGER.debug(f'Created memory_set: {memory_set}')
            self.replay_memory.append(memory_set)
            network.request_state(self, memory_set)
            packet.reward_request(memory_set)

            self.data['memory_set'].append(memory_set)

        if not network.tick % self.NETWORK_UPDATE_TICK:
            LOGGER.debug('Updating target network')
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def transmit(self, network):
        raise Exception('Q-LEARNING IMPLEMENTATION ONLY FOR RELAYING')

    def optimize_model(self):
        if len(self.replay_memory) < self.BATCH_SIZE:
            LOGGER.debug('Not enough replay memory, continuing..')
            return

        # Get a list of replay memories 
        transitions = self.replay_memory.sample(self.BATCH_SIZE)
        if len(transitions) == 0:
            LOGGER.warning('Not enough transitions were given')
            return
        LOGGER.debug(f'Size of samples retrieved: {len(transitions)}')
        LOGGER.debug(f'Optimizing model for node {self}')
        # Turn into list of list (tensor?)
        state_batch = torch.cat([t['state'] for t in transitions]).reshape(len(transitions), self.max_neighbors**2)
        action_batch = torch.cat([t['action'] for t in transitions])
        reward_batch = torch.cat([t['reward'] for t in transitions]).reshape(len(transitions), 1)
        next_state_batch = torch.cat([t['next_state'] for t in transitions]).reshape(len(transitions), self.max_neighbors**2)

        # Tensor containing the q-value for every action taken in every state
        state_action_values = self.policy_net(state_batch.float()).gather(1, action_batch)

        next_state_values = self.target_net(next_state_batch.float()).max(1)[0].detach()

        expected_state_action_values = (next_state_values * self.GAMMA) + reward_batch

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
        self.data['loss'].append(loss.tolist())

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

        LOGGER.debug('Finished Optimizing!')


    def get_state(self, network):
        """
        """
        LOGGER.debug(f'Getting state for node {self}')
        state = np.zeros(self.max_neighbors**2)  # Array consists of neighbors and their neighbors as well
        # Collect packet size info for all neighbors, and neighbor of neighbors
        index = 0
        for neighbor in nx.neighbors(network, self):
            if index >= len(state):
                break
            state[index] = len(neighbor.queue)
            for neighbor_in_law in nx.neighbors(network, neighbor):
                if index >= len(state) - 1:
                    break
                index+=1
                state[index] = len(neighbor_in_law.queue)
            index+=1

        LOGGER.debug(f'State for {self} at tick {network.tick}: {state}')
        state = torch.from_numpy(state)
        return state

    def __del__(self):
        torch.save(self.policy_net.state_dict(), './QOFFLOADING')
