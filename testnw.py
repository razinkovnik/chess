import torch
from torch import nn, reshape
from utils import root_folder
from board import Board
from networks import ConvEncoderDecoder

board = Board()

x = board.to_vector()
x = torch.tensor(x, dtype=torch.float).unsqueeze(0)
model = ConvEncoderDecoder()
print(x)
print(model(x))
