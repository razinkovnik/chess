from networks import SimpleLeaner
from game_analysis import *
from notation import Notation


def go(notation):
    game.board.play(Notation(game.board, 0, notation))
    game.board.show()


model = SimpleLeaner()
model.load()

game = Game(model)

go("e4")

game.show()
