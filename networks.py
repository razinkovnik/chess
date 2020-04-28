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


# Примитивная нейронка
class SimpleLinear(Base):
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(64 * 6, 64)
        self.linear2 = nn.Linear(64, 64 * 6)
        self.tanh = nn.Tanh()
        self.loss = nn.MSELoss(reduction="sum")
        self.name = "simple"

    def forward(self, x, target=None):
        x = self.tanh(self.linear1(x))
        out = self.tanh(self.linear2(x))
        if target is not None:
            loss = self.loss(out, target)
            return loss, out
        else:
            return out


class SimpleConv2d(Base):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(6, 64, 3)
        self.pool = nn.MaxPool2d(2)
        self.linear = nn.Linear(576, 64*6)
        self.tanh = nn.Tanh()
        self.loss = nn.MSELoss(reduction="sum")
        self.name = "conv"

    def forward(self, x, target=None):
        x = reshape(x, [-1, 6, 8, 8])
        x = self.conv(x)
        x = self.pool(x)
        x = reshape(x, [-1, 576])
        x = self.linear(x)
        out = self.tanh(x)
        if target is not None:
            loss = self.loss(out, target)
            return loss, out
        else:
            return reshape(out, [-1])


class ConvEncoderDecoder(Base):
    def __init__(self):
        super().__init__()
        n_chanel_in = 1
        n_chanel_out = 64
        self.conv1 = nn.Conv2d(6, n_chanel_in, 1)
        self.conv2 = nn.Conv2d(n_chanel_in, n_chanel_out, 3, padding=1)
        self.conv3 = nn.Conv2d(n_chanel_out, n_chanel_out, 3)
        self.pool = nn.MaxPool2d(2)
        self.linear = nn.Linear(n_chanel_out, n_chanel_out * 4)
        self.decoder = nn.Linear(n_chanel_out*4, 64 * 6)
        self.tanh = nn.Tanh()
        self.loss = nn.MSELoss(reduction="sum")
        self.name = "convende"

    def forward(self, x, target=None):
        y = reshape(x, [-1, 6, 8, 8])
        y = self.conv1(y)
        y = y + self.conv2(y)
        y = self.pool(y)
        y = self.conv3(y)
        y = self.pool(y)
        y = reshape(y, [x.shape[0], -1])
        y = self.tanh(self.linear(y))
        out = self.tanh(self.decoder(y))
        # out = x + y
        if target is not None:
            loss = self.loss(out, target)
            return loss, out
        else:
            return reshape(out, [-1])
