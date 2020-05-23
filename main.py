import time
from chess_com import ChessCom
from visual import show
from minimax import min_max_alpha_betta_search, Node
import ga
from score import total_score


def select_node(root):
    nodes = list(filter(lambda node: node.score == root.score, root.leaves))
    for node in nodes:
        w_score, b_score = total_score(node.board)
        node.score = w_score - b_score
    return max(nodes, key=lambda node: node.score) if root.color == "w" else min(nodes, key=lambda node: node.score)


def step(chess: ChessCom):
    moves = chess.read_moves()
    chess.update_board(moves)
    root = Node("b", chess.board)
    if chess.last_step:
        fig, end = chess.last_step.fig, chess.last_step.pos_to
        if fig == "bp":
            root.last_step = end
    root.can_castling = chess.can_castling
    min_max_alpha_betta_search(root, 1, 2)
    node = select_node(root)
    chess.can_castling = node.can_castling
    print(node.fig, node.start, node.end)
    chess.move(node.start, node.end)


chess = ChessCom()
time.sleep(3)
chess.flip_board()


# chess.flip_board()
# move_count = 0


# while True:
#     time.sleep(1)
#     moves = chess.read_moves()
#     if move_count < len(moves):
#         chess.update_board(moves)
#         next_move = game.predict(chess.board)
#         print(next_move)
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
