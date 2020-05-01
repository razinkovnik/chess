from collections import namedtuple
import pandas as pd

import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader, SequentialSampler

from utils import root_folder

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
        return torch.tensor([cur], dtype=torch.float), torch.tensor([nxt], dtype=torch.long)


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


train_df = pd.read_csv(f'{root_folder}/boardmoves.csv')
train_iter = build_data_iterator(MyDataset(train_df), 512)
