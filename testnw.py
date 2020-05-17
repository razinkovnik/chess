from data import train_iter
from board import Board
from score import total_score
import ga
from minimax import min_max_alpha_betta_search, Node
from visual import show
import time

batch = next(iter(train_iter))
inputs, targets = batch
n = 135
state = [int(x) for x in inputs[n].tolist()]
x, target = inputs[n].unsqueeze(0), targets[0].unsqueeze(0)
board = Board()
board.from_state(state)
show(board)

# noinspection DuplicatedCode
if __name__ == '__main__':
    timer = time.time()
    root = Node("b", board)
    min_max_alpha_betta_search(root, 1, 2)
    nodes = list(filter(lambda node: node.score == root.score, root.leaves))
    nodes = [node for node in nodes if not ga.test_check(node.board, node.fig[0], node.fig, node.start, node.end)]
    if len(nodes) > 1:
        for node in nodes:
            w_score, b_score = total_score(node.board)
            node.score = w_score - b_score
    elif len(nodes) == 0:
        raise RuntimeError("не найдено ходов")
    node = min(nodes, key=lambda node: node.score)
    show(node.board)
    spend_time = time.time() - timer
    print(root.score, spend_time)
