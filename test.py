from networks import Model
from game import *
from notation import Notation


def go(move):
    board.play(Notation(board, 0, move))
    board.show()


model = Model()
model.load()
model.cuda()
move_count = 0

board = Board()

go("e4")

# predict
game = Game(model)


def show():
    next_move = game.predict(board)
    print(next_move)
    fig, pos_from, pos_to, prob = next_move
    board.move(fig, pos_from, pos_to)
    board.show()
# while True:
#     time.sleep(1)
#     moves = chess.read_moves()
#     if move_count < len(moves):
#         chess.update_board(moves)
#         next_move = chess.game.predict()
#         if not next_move:
#             break
#         fig, pos_from, pos_to, prob = next_move
#         if fig == "O-O":
#             pos_from, pos_to = "e8", "g8"
#         elif fig == "O-O-O":
#             pos_from, pos_to = "e8", "c8"
#         print(f"{fig} {pos_from}-{pos_to}, prob = {prob}")
#         chess.move(pos_from, pos_to)
#         move_count = len(moves)

# TODO: контроль рокировки, контроль пешки / битое поле
