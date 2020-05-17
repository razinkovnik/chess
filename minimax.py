from board import Board
from score import total_score, material_score
import ga
from typing import List


def get_half_steps(color, board, test_check=True):
    half_steps = []
    for fig in [color + fig for fig in ["p", "n", "b", "r", "q", "k"]]:
        start_positions = list(board.chess[fig])
        for start in start_positions:
            if fig[1] == "q":
                positions = ga.queen_move_variants(start)
                positions = ga.filter_queen_move(board, color, start, positions)
            elif fig[1] == "r":
                positions = ga.rook_move_variants(start)
                positions = ga.filter_rook_move(board, color,start, positions)
            elif fig[1] == "n":
                positions = ga.knight_move_variants(start)
                positions = ga.filter_knight_move(board, color, positions)
            elif fig[1] == "b":
                positions = ga.bishop_move_variants(start)
                positions = ga.filter_bishop_move(board, color, start, positions)
            elif fig[1] == "k":
                positions = ga.king_move_variants(start)
                positions = ga.filter_king_move(board, color, positions)
            else:
                if fig == "bp":
                    positions = ga.black_pawn_move_variants(start)
                else:
                    positions = ga.white_pawn_move_variants(start)
                positions = ga.filter_pawn_move(board, color, start, positions)
            if test_check:
                positions = list(filter(lambda pos: not ga.test_check(board, color, fig, start, pos), positions))
            half_steps += [(fig, start, end) for end in positions]
    return half_steps


class Node:
    def __init__(self, color, board, fig=None, start=None, end=None, root=None):
        self.color = color
        self.fig = fig
        self.board = board.clone()
        if start:
            self.board.move(self.fig, start, end)
        self.start = start
        self.end = end
        self.score = None
        self.root = root
        self.leaves = []

    def fill(self, test_check=True):
        moves = get_half_steps(self.color, self.board, test_check)
        self.leaves = [Node(ga.opp_color(self.color), self.board, fig, start, end, self) for (fig, start, end) in moves]
        return self.leaves


def fill_nodes(nodes: List[Node], n=1):
    while n > 0:
        nodes = [leaf for node in nodes for leaf in node.fill()]
        n -= 1


# counter = 0


def material(board: Board) -> int:
    return material_score("w", board) - material_score("b", board)


def min_max_alpha_betta_search(root: Node, n, count=2, alpha=-1000, betta=1000, test_check=True):
    # global counter
    if count == 0:
        root.score = material(root.board)
        # counter += 1
    else:
        if not root.score:
            root.score = betta if n % 2 else alpha
        if len(root.leaves) == 0:
            root.fill(test_check)
        for node in root.leaves:
            min_max_alpha_betta_search(node, n + 1, count - 1, alpha, betta)
            if n % 2:
                if root.score > node.score:
                    root.score = node.score
                    if root.score < alpha:
                        return
                    betta = min(betta, root.score)
            else:
                if root.score < node.score:
                    root.score = node.score
                    if root.score > betta:
                        return
                    alpha = max(alpha, root.score)
