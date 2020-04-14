from functools import reduce

import pandas as pd
from tqdm import tqdm

from board import Board
from notation import Notation
from utils import root_folder

# Собрать вектор доски и последующий ход в словарь
gamedata = pd.read_csv(f'{root_folder}/games.csv')

debug = False
boards = []
for moves in tqdm(gamedata.moves):
    board = Board()
    for i, move in enumerate(moves.split()):
        debug and print(i + 1, move)
        notation = Notation(board, i % 2, move)
        debug and print(notation)
        board.play(notation)
        debug and board.show()
        board_vector = reduce(lambda a, b: f'{a} {b}', board.to_vector())
        if i % 2 == 0:
            last_board = board_vector
        else:
            # noinspection PyUnboundLocalVariable
            boards += [[last_board, board_vector]]
df = pd.DataFrame(boards)
df.drop_duplicates()
df.to_csv(f'{root_folder}/boardmoves.csv')
