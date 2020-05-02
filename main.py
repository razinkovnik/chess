import time

from chess_com import ChessCom
from networks import Model
from game import Game

chess = ChessCom()
time.sleep(3)
chess.flip_board()
move_count = 0

model = Model()
model.load()
model.cuda()
model.eval()
game = Game(model)

while True:
    time.sleep(1)
    moves = chess.read_moves()
    if move_count < len(moves):
        chess.update_board(moves)
        next_move = game.predict(chess.board)
        print(next_move)
        if not next_move:
            break
        fig, pos_from, pos_to, prob = next_move
        if fig == "O-O":
            pos_from, pos_to = "e8", "g8"
        elif fig == "O-O-O":
            pos_from, pos_to = "e8", "c8"
        print(f"{fig} {pos_from}-{pos_to}, prob = {prob}")
        chess.move(pos_from, pos_to)
        move_count = len(moves)

# TODO: контроль рокировки, контроль пешки / битое поле
