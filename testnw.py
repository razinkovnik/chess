from data import train_iter
from board import Board
from score import total_score

batch = next(iter(train_iter))
inputs, targets = batch
n = 135
state = [int(x) for x in inputs[n].tolist()]
x, target = inputs[n].unsqueeze(0), targets[0].unsqueeze(0)
board = Board()
board.from_state(state)
board.show()


# SCORE
w_score = total_score(board)


print("total_score", total_score(board))
