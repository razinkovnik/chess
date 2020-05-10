import torch
from torch import nn, reshape
from utils import root_folder

device = torch.device("cuda")


class Base(nn.Module):
    def __init__(self):
        super().__init__()
        self.name = ""

    def load(self):
        self.load_state_dict(torch.load(f"{root_folder}/{self.name}.model"))
        self.to(device)
        self.eval()

    def save(self):
        torch.save(self.state_dict(), f'{root_folder}/{self.name}.model')


class Model(Base):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(6, 1, 1)
        self.encoder = nn.Linear(1*8*8, 16)
        self.decoder = nn.Linear(16, 64)
        self.relu = nn.ReLU()
        self.loss = nn.CrossEntropyLoss()

    def forward(self, x, target=None):
        x = reshape(x, [-1, 6, 8, 8])
        x = self.conv(x)
        x = reshape(x, [-1, 1*8*8])
        x = self.encoder(x)
        x = self.decoder(x)
        y1 = self.relu(x)
        y2 = self.relu(-x)
        if target is not None:
            pos_from, pos_to = target.t()
            l1 = self.loss(y1, pos_from)
            l2 = self.loss(y2, pos_to)
            return l1 + l2
        else:
            y1 = nn.functional.softmax(y1, 1)
            y2 = nn.functional.softmax(y2, 1)
            return reshape(y1, [-1]), reshape(y2, [-1])


class Model2(Base):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(6, 1, 1)
        self.conv2 = nn.Conv2d(1, 8, 2)
        self.conv3 = nn.Conv2d(8, 16, 3)
        self.linear1 = nn.Linear(16*5*5, 1024)
        # self.linear2 = nn.Linear(1024, 256)
        self.output = nn.Linear(1024, 64)
        self.relu = nn.ReLU()
        # self.tanh = nn.Tanh()
        self.loss = nn.CrossEntropyLoss()
        self.dropout1 = nn.Dropout(0.5)
        # self.dropout2 = nn.Dropout(0.2)

    def forward(self, x, target=None):
        x = reshape(x, [-1, 6, 8, 8])
        x = self.conv(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = reshape(x, [-1, 16*5*5])
        x = self.linear1(x)
        x = self.dropout1(x)
        x = self.relu(x)
        # x = self.linear2(x)
        # x = self.dropout2(x)
        # x = self.relu(x)
        x = self.output(x)
        # x = self.dropout(x)
        y1 = self.relu(x)
        y2 = self.relu(-x)
        if target is not None:
            pos_from, pos_to = target.t()
            l1 = self.loss(y1, pos_from)
            l2 = self.loss(y2, pos_to)
            return l1 + l2
        else:
            y1 = nn.functional.softmax(y1, 1)
            y2 = nn.functional.softmax(y2, 1)
            return reshape(y1, [-1]), reshape(y2, [-1])
