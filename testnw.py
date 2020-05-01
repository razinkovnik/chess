import torch
from torch import nn, reshape
from utils import root_folder
from board import Board
from networks import Model
from notation import Notation
from utils import *
from data import train_iter

batch = next(iter(train_iter))
inputs, targets = batch
x, target = inputs[0].unsqueeze(0), targets[0].unsqueeze(0)

model = Model().cuda()
y = model(x, target)
