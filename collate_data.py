from functools import reduce

import pandas as pd
from tqdm import tqdm

from board import Board
from notation import Notation
from utils import *

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
            pos_from, pos_to = notation.pos_from, notation.pos_to
            if "O-O-O" in move:
                pos_from, pos_to = "e8", "c8"
            elif "O-O" in move:
                pos_from, pos_to = "e8", "g8"
            pos_from, pos_to = pos2num(pos_from), pos2num(pos_to)
            # noinspection PyUnboundLocalVariable
            boards += [[last_board, f"{pos_from} {pos_to}"]]
df = pd.DataFrame(boards)
# df.drop_duplicates()
df.to_csv(f'{root_folder}/boardmoves.csv')
