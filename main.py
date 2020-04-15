import time

from chess_com import ChessCom
from networks import SimpleLeaner
from game_analysis import *

model = SimpleLeaner()
model.load()

chess = ChessCom()
time.sleep(3)
chess.flip_board()
chess.update_board()
chess.predict_update()
time.sleep(3)
