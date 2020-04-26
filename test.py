from networks import SimpleLinear, SimpleConv2d
from game_analysis import *
from notation import Notation


def go(move):
    game.board.play(Notation(game.board, 0, move))
    game.board.show()


model = SimpleConv2d()
model.cuda()
move_count = 0

board = Board()

game = Game(model)
game.board = board
go("e4")
next_state = game.show()

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
