import random
import logging
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)

class PyTorchQNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        # Define NN here
        self.fc1 = nn.Linear(16, 12)
        self.fc2 = nn.Linear(12, 8)
        self.fc3 = nn.Linear(8, 4)
        self.fc4 = nn.Linear(4, 2)

    # This could be called with either one element, or with a batch (for optimization)
    # so, it will return a tensor [[q-values], [q-values2],...]
    def forward(self, x):
        # Define flow here
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        return x

class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
        self.counter = 0

    def append(self, element):
        self.memory.append(element)
        self.counter += 1

    def sample(self, sample_count):
        '''
        Sample replays that have been fully filled out
        (no None values, etc)
        '''
        LOGGER.debug(f'Current samples: {self.memory}')
        sample_list = random.sample(self.memory, sample_count)
        samples = []
        count = 0
        for s in sample_list:
            if  s['next_state'] is None or s['reward'] is None:
                continue
            else:
                samples.append(s)

        return samples

    def __len__(self):
        return len(self.memory)
