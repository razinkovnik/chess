import time
from chess_com import ChessCom
from visual import show
from minimax import min_max_alpha_betta_search, Node
import ga
from score import total_score


# noinspection DuplicatedCode
def predict(board, color):
    root = Node(color, board)
    min_max_alpha_betta_search(root, "wb".index(color), 2)
    nodes = list(filter(lambda node: node.score == root.score, root.leaves))
    nodes = [node for node in nodes if not ga.test_check(node.board, node.fig[0], node.fig, node.start, node.end)]
    if len(nodes) > 1:
        for node in nodes:
            w_score, b_score = total_score(node.board)
            node.score = w_score - b_score
    elif len(nodes) == 0:
        raise RuntimeError("не найдено ходов")
    node = min(nodes, key=lambda node: node.score)
    return node.start, node.end


def step():
    moves = chess.read_moves()
    chess.update_board(moves)
    chess.move(*predict(chess.board, "b"))


chess = ChessCom()
time.sleep(3)
chess.flip_board()
move_count = 0


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
