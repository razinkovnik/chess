import torch

from tqdm import tqdm
# from IPython.display import clear_output
import matplotlib.pyplot as plt

from networks import Model2
from utils import *

from data import train_iter

# Тренируем
model = Model2()
model.load()
model.cuda()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

max_grad_norm = 1.0
model.train()
losses = []
i = 0
for batch in tqdm(train_iter):
    loss = model(batch.cur, batch.nxt)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
    optimizer.step()
    optimizer.zero_grad()
    i += 1
    losses += [loss.detach().item()]
plt.plot(losses)
plt.title("Training loss")
plt.xlabel("Batch")
plt.ylabel("Loss")
plt.show()
model.save()
