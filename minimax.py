from board import Board
from score import total_score, material_score, king_side_score
import ga
from typing import List
from utils import *


def get_half_steps(color, board, move_throw_attacked_field, test_check=True):
    half_steps = []
    for fig in [color + fig for fig in ["p", "n", "b", "r", "q", "k"]]:
        start_positions = list(board.chess[fig])
        for start in start_positions:
            if fig[1] == "q":
                positions = ga.queen_move_variants(start)
                positions = ga.filter_queen_move(board, color, start, positions)
            elif fig[1] == "r":
                positions = ga.rook_move_variants(start)
                positions = ga.filter_rook_move(board, color, start, positions)
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
                positions = ga.filter_pawn_move(board, color, start, positions, move_throw_attacked_field)
            if test_check:
                positions = list(filter(lambda pos: not ga.test_check(board, color, fig, start, pos), positions))
            half_steps += [(fig, start, end) for end in positions]
    return half_steps


def line(start, end):
    start, end = pos2num(start), pos2num(end)
    start, end = min(start, end), max(start, end)
    if (end - start) % 7 == 0:
        k = 7
    elif (end - start) % 8 == 0:
        k = 8
    else:
        k = 9
    return [num2pos(end - k * i) for i in range((end - start) // k + 1)]


def can_castling_pawns(board, opp_color, type_castling: str):
    pawns = set(board.chess[opp_color + "p"])
    row = 2 if opp_color == "b" else 7
    if type_castling == "short" and len(pawns.intersection([f"e{row}", f"f{row}", f"g{row}", f"h{row}"])):
        return False
    if type_castling == "long" and len(pawns.intersection([f"a{row}", f"b{row}", f"c{row}", f"d{row}", f"e{row}"])):
        return False
    return True


def can_castling_knights(board, opp_color, type_castling: str):
    knights = set(board.chess[opp_color + "n"])
    row1 = 2 if opp_color == "b" else 7
    row2 = 3 if opp_color == "b" else 6
    if type_castling == "short":
        if len(knights.intersection([f"d{row1}", f"e{row1}", f"e{row2}", f"f{row2}", f"g{row2}", f"h{row2}"])):
            return False
    if type_castling == "long":
        if len(knights.intersection(
                [f"a{row1}", f"b{row1}", f"d{row1}", f"e{row1}", f"f{row1}", f"a{row2}", f"b{row2}", f"c{row2}",
                 f"d{row2}",
                 f"e{row2}"])):
            return False
    return True


def can_castling(board, opp_color, type_castling: str):
    return can_castling_lines(board, opp_color, type_castling) and can_castling_pawns(board, opp_color,
                                                                                      type_castling) and can_castling_pawns(
        board, opp_color, type_castling) and can_castling_knights(board, opp_color, type_castling)


def can_castling_lines(board, opp_color, type_castling: str):
    if opp_color == "w":
        if type_castling == "short":
            lines = [("a6", "f1"), ("a7", "g1"), ("f1", "h3"), ("g1", "h2"), ("f8", "f1"), ("g8", "g1")]
        else:
            lines = [("a2", "b1"), ("a3", "c1"), ("a4", "d1"), ("b1", "h7"), ("c1", "a6"), ("d1", "a5"),
                     ("b1", "b8"), ("c1", "c8"), ("d1", "d8"), ("e1", "e8")]
        lines = [line(start, end) for (start, end) in lines]
    else:
        if type_castling == "short":
            lines = [("a3", "f8"), ("a2", "g8"), ("f8", "h6"), ("g8", "h7"), ("f8", "f1"), ("g8", "g1")]
        else:
            lines = [("a7", "b8"), ("a6", "c8"), ("a5", "d8"), ("b8", "h2"), ("c8", "h3"), ("d8", "h4"),
                     ("b1", "b8"), ("c1", "c8"), ("d1", "d8"), ("e1", "e8")]
        lines = [line(start, end)[::-1] for (start, end) in lines]
    d_figs = [opp_color + "b", opp_color + "q"]
    l_figs = [opp_color + "r", opp_color + "q"]
    d_figs = [el for fig in d_figs for el in board.chess[fig]]
    for fig in d_figs:
        for l in lines[:-2]:
            if fig in l:
                if board.is_clear_diagonal(fig, l[-1]):
                    return False
    for fig in l_figs:
        for l in lines[-2:]:
            if fig in l:
                if board.is_clear_line(fig, l[-1]):
                    return False
    return True


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
        self.can_castling = self.__can_castling_init()

    def __can_castling_init(self):
        can_castling = True, True
        if self.root and self.root.root:
            can_castling = self.root.root.can_castling
        if self.fig:
            if self.fig[1] == "k":
                can_castling = False, False
            if self.fig == "wr":
                if self.start == "a1":
                    can_castling = False, can_castling[1]
                if self.start == "h1":
                    can_castling = can_castling[1], False
            if self.fig == "br":
                if self.start == "a8":
                    can_castling = False, can_castling[1]
                if self.start == "h8":
                    can_castling = can_castling[1], False
        return can_castling

    def __fill_castling(self, opp_color, short_castling, long_castling):
        fields = set([pos for positions in self.board.chess.values() for pos in positions])
        row = [1, 8]['wb'.index(self.color)]
        if short_castling and not len(fields.intersection({f"f{row}", f"g{row}"})) and can_castling(self.board,
                                                                                                    opp_color, "short"):
            node = Node(opp_color,
                        self.board.move(f"{self.color}k", f"e{row}", f"g{row}").move(f"{self.color}r", f"h{row}",
                                                                                     f"f{row}"), f"{self.color}k",
                        f"e{row}", f"g{row}")
            self.leaves.append(node)
        if long_castling and not len(fields.intersection({f"b{row}", f"c{row}", f"d{row}"})) and can_castling(
                self.board, opp_color, "long"):
            node = Node(opp_color,
                        self.board.move(f"{self.color}k", f"e{row}", f"d{row}").move(f"{self.color}r", f"a{row}",
                                                                                     f"e{row}"), f"{self.color}k",
                        f"e{row}", f"d{row}")
            self.leaves.append(node)

    def fill(self, test_check: bool):
        can_castling = True, True
        if self.root and self.root.root:
            can_castling = self.root.root.can_castling
        short_castling, long_castling = can_castling
        if self.root and self.root.fig and self.root.fig[1] == "p":
            move_throw_attacked_field = self.root.end
        else:
            move_throw_attacked_field = None
        moves = get_half_steps(self.color, self.board, move_throw_attacked_field, test_check)
        opp_color = ga.opp_color(self.color)
        self.leaves = [Node(opp_color, self.board, fig, start, end, self) for (fig, start, end) in moves]
        if short_castling or long_castling:
            self.__fill_castling(opp_color, short_castling, long_castling)
        return self.leaves


class Counter:
    def __init__(self):
        self.counter = 0


counter = Counter()


def material(board: Board) -> int:
    return material_score("w", board) - material_score("b", board)


def min_max_alpha_betta_search(root: Node, n, count=2, alpha=-1000, betta=1000, test_check=True):
    global counter
    if count == 0:
        root.score = material(root.board)
        counter.counter += 1
    else:
        if not root.score:
            root.score = betta if n % 2 else alpha
        if len(root.leaves) == 0:
            root.fill(test_check)
        if len(root.leaves) == 0:
            # todo проверить на пат
            root.score = -1000 if n % 2 else 1000
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
