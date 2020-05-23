from data import train_iter
from board import Board
from score import total_score
import ga
from minimax import min_max_alpha_betta_search, Node, counter
from visual import show
import time
from notation import Notation
import random as rnd
from notation import Notation

batch = next(iter(train_iter))
inputs, targets = batch
n = 128
state = [int(x) for x in inputs[n].tolist()]
x, target = inputs[n].unsqueeze(0), targets[0].unsqueeze(0)
board = Board()
board.from_state(state)
# board.remove("b5")
# board.add("bp", "f2")
show(board)


def select_node(root):
    nodes = list(filter(lambda node: node.score == root.score, root.leaves))
    for node in nodes:
        w_score, b_score = total_score(node.board)
        node.score = w_score - b_score
    return max(nodes, key=lambda node: node.score) if root.color == "w" else min(nodes, key=lambda node: node.score)


def short_root_leaves(root, limit):
    nodes = sorted(root.leaves, key=lambda node: node.score,
                   reverse=root.color == "w")
    best_score = nodes[0].score
    best_nodes = [node for node in nodes if node.score == best_score]
    if len(best_nodes) >= limit:
        rnd.shuffle(best_nodes)
        root = best_nodes[limit - 1]
    max_score = nodes[:limit][-1].score
    if root.color == "w":
        nodes = [node for node in root.leaves if node.score >= max_score]
    else:
        nodes = [node for node in root.leaves if node.score <= max_score]
    rnd.shuffle(nodes)
    nodes = nodes[:limit - len(best_nodes)]
    root.leaves = best_nodes + nodes
    for node in root.leaves:
        node.score = None
    root.score = None


def short_leaves(root, limit):
    if root.leaves:
        root.leaves = [node for node in root.leaves if node.score is not None]
        if len(root.leaves) >= limit:
            short_root_leaves(root, limit)
            for node in root.leaves:
                short_leaves(node, limit)


def go(color: str, deep=2):
    timer = time.time()
    assert color == "w" or color == "b"
    root = Node(color, board)
    color = 0 if color == "w" else 1
    min_max_alpha_betta_search(root, color, 2)
    short_leaves(root, deep)
    # counter.counter = 0
    # min_max_alpha_betta_search(root, color, 4)
    # print(counter.counter)
    node = select_node(root)
    print(root.score, node.score)
    board.move(node.fig, node.start, node.end)
    show(board)
    print(time.time() - timer)
