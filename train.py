from collections import namedtuple
import pandas as pd

import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader, SequentialSampler
from tqdm import tqdm
# from IPython.display import clear_output
import matplotlib.pyplot as plt

from networks import SimpleLeaner
from utils import *

device = torch.device("cuda")


class MyDataset(Dataset):
    def __init__(self, df):
        self.df = df

    def __len__(self):
        return len(self.df)

    @staticmethod
    def __row2board(row):
        return [int(x) for x in row.split()]

    def __getitem__(self, index):
        cur = MyDataset.__row2board(self.df['0'].iloc[index])
        nxt = MyDataset.__row2board(self.df['1'].iloc[index])
        return torch.tensor([cur], dtype=torch.float), torch.tensor([nxt], dtype=torch.float)


Batch = namedtuple(
    "Batch", ["cur", "nxt"]
)


def collate(data):
    cur_list, nxt_list = [], []
    for cur, nxt in data:
        cur_list.append(cur)
        nxt_list.append(nxt)
    return Batch(
        cur=torch.cat(cur_list).to(device),
        nxt=torch.cat(nxt_list).to(device),
    )


def build_data_iterator(dataset, batch_size):
    sampler = SequentialSampler(dataset)
    iterator = DataLoader(
        dataset, sampler=sampler, batch_size=batch_size, collate_fn=collate
    )
    return iterator


# Тренируем
train_df = pd.read_csv(f'{root_folder}/boardmoves.csv')
train_iter = build_data_iterator(MyDataset(train_df), 512)

model = SimpleLeaner()
model.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

max_grad_norm = 1.0
model.train()
losses = []
i = 0
for batch in tqdm(train_iter):
    loss = model(batch.cur, batch.nxt)[0]
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
    optimizer.step()
    optimizer.zero_grad()
    i += 1
    losses += [loss.detach().item()]
    if i % 10 == 0:
        # clear_output(wait=True)
        plt.plot(losses)
        plt.title("Training loss")
        plt.xlabel("Batch")
        plt.ylabel("Loss")
        plt.show()

torch.save(model.state_dict(), f'{root_folder}/simple.model')
