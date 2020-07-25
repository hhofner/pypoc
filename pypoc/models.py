import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

class PytorchQNetwork:
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
