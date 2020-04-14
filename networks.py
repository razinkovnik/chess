import torch
from torch import nn
from utils import root_folder

device = torch.device("cuda")


# Примитивная нейронка
class SimpleLeaner(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(64 * 6, 64)
        self.linear2 = nn.Linear(64, 64 * 6)
        self.tanh = nn.Tanh()
        self.loss = nn.MSELoss(reduction="sum")

    def forward(self, x, target=None):
        x = self.tanh(self.linear1(x))
        out = self.tanh(self.linear2(x))
        if target is not None:
            loss = self.loss(out, target)
            return loss, out
        else:
            return out

    def load(self):
        self.load_state_dict(torch.load(f"{root_folder}/simple.model"))
        self.to(device)
        self.eval()
