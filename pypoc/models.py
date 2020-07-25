from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

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
        #TODO: Optimize
        print("Getting sample")
        sample_list = []
        count = 0
        error_count = 0
        while(count < sample_count):
            sample = random.sample(self.memory)
            if not sample['next_state'] or not sample['reward']:
                error_count += 1
            else:
                sample_list.append(sample)
                count += 1
            if error_count >= 50:
                print('Error count exceeded 50')
                print(f'Memory list: {self.memory}')
                raise Exception('Exceeded allowed amount of tries, consider rewriting this method')
        return random.sample(self.memory, sample_count)

    def __len__(self):
        return len(self.memory)


