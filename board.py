from functools import reduce

from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from utils import *
import numpy as np


class Board:
    def __init__(self):
        self.board = None
        self.w = 109
        self.chess = {
            "wp": ["a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2"],
            "wr": ["a1", "h1"],
            "wn": ["b1", "g1"],
            "wb": ["c1", "f1"],
            "wq": ["d1"],
            "wk": ["e1"],
            "bp": ["a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7"],
            "br": ["a8", "h8"],
            "bn": ["b8", "g8"],
            "bb": ["c8", "f8"],
            "bq": ["d8"],
            "bk": ["e8"],
        }
        self.figs = {}
        for fig in self.chess.keys():
            self.figs[fig] = Image.open(f'{root_folder}/{fig}.png', 'r').convert('RGBA')

    def __setup_board(self):
        w = self.w
        board = Image.new('RGBA', (w * 8, w * 8))
        d = ImageDraw.Draw(board)
        black_color = "#769656"
        white_color = "#eeeed2"

        for j in range(1, 9):
            for i in range(1, 9):
                shape = [(w * (i - 1), w * (j - 1)), (w * i, w * j)]
                color = white_color if (i + j) % 2 == 0 else black_color
                d.rectangle(shape, fill=color)
        return board

    def __paste_fig2pos(self, fig, pos):
        x, y = "abcdefgh".index(pos[0]), 8 - int(pos[1])
        self.board.paste(self.figs[fig], (self.w * x, self.w * y), mask=self.figs[fig])

    def show(self):
        self.board = self.__setup_board()
        for fig in self.chess.keys():
            for pos in self.chess[fig]:
                self.__paste_fig2pos(fig, pos)
        fig, ax = plt.subplots()
        ax.imshow(np.asarray(self.board))
        ax.set_title("ход")
        fig.set_figwidth(7)  # ширина и
        fig.set_figheight(7)  # высота "Figure"
        plt.show()

    def remove(self, pos):
        for fig, positions in self.chess.items():
            if pos in positions:
                self.chess[fig].remove(pos)
                return

    def add(self, fig, pos):
        self.chess[fig] += [pos]

    def move(self, fig, pos_from, pos_to):
        self.remove(pos_from)
        self.add(fig, pos_to)

    def find_pawn_position(self, fig, pos_to):
        color = 0 if fig[0] == "w" else 1
        col, row = pos_to
        delta = [-1, 1][color]
        row = int(row) + delta
        pos_from = f"{col}{row}"
        if pos_from not in self.chess[fig]:
            pos_from = f"{col}{row + delta}"
        return pos_from

    def find_rook_position(self, fig, pos_to):
        col, row = pos_to
        positions = filter(lambda pos: pos[0] == col or pos[1] == row, self.chess[fig])
        positions = list(filter(lambda pos: self.is_clear_line(pos, pos_to), positions))
        return self.select_move(fig, pos_to, positions)

    def find_queen_position(self, fig, pos_to):
        positions = list(
            filter(lambda p1: self.is_clear_line(p1, pos_to) or self.is_clear_diagonal(p1, pos_to), self.chess[fig]))
        return self.select_move(fig, pos_to, positions)

    def find_bishop_position(self, fig, pos_to):
        positions = list(filter(lambda pos: self.is_clear_diagonal(pos, pos_to), self.chess[fig]))
        return self.select_move(fig, pos_to, positions)

    def find_knight_position(self, fig, pos_to):
        col, row = pos_to
        col = "abcdefgh".index(col)
        row = int(row) - 1
        positions = [(col - 1, row - 2), (col - 1, row + 2), (col + 1, row - 2), (col + 1, row + 2), (col - 2, row - 1),
                     (col - 2, row + 1), (col + 2, row - 1), (col + 2, row + 1)]
        positions = filter(lambda pos: -1 < pos[0] < 8 and -1 < pos[1] < 8, positions)
        positions = map(lambda pos: ("abcdefgh"[pos[0]], pos[1] + 1), positions)
        positions = [f"{c}{r}" for c, r in positions]
        positions = list(set(self.chess[fig]) & set(positions))
        return self.select_move(fig, pos_to, positions)

    def select_move(self, fig, pos_to, positions):
        if len(positions) > 1:
            p_k = self.chess[fig[0] + "k"][0]
            op = "wb"["bw".index(fig[0])]
            for pos_from in positions:
                test = False
                self.chess[fig].remove(pos_from)
                self.add(fig, pos_to)
                for op_p_r in self.chess[op + "r"]:
                    if self.is_clear_line(op_p_r, p_k):
                        test = True
                if not test:
                    for op_p_q in self.chess[op + "q"]:
                        if self.is_clear_line(op_p_q, p_k) or self.is_clear_diagonal(op_p_q, p_k):
                            test = True
                if not test:
                    for op_p_b in self.chess[op + "b"]:
                        if self.is_clear_diagonal(op_p_b, p_k):
                            test = True
                self.add(fig, pos_from)
                self.chess[fig].remove(pos_to)
                if not test:
                    return pos_from
        return positions[0]

    def is_clear_line(self, p1, p2):
        p1, p2 = sorted([p1, p2])
        positions = [p for lst in self.chess.values() for p in lst]
        if p1[1] == p2[1]:
            cols = "abcdefgh"
            for i in range(cols.index(p1[0]) + 1, cols.index(p2[0])):
                if f"{cols[i]}{p1[1]}" in positions:
                    return False
        elif p1[0] == p2[0]:
            for i in range(int(p1[1]) + 1, int(p2[1])):
                if f"{p1[0]}{i}" in positions:
                    return False
        else:
            return False
        return True

    def is_clear_diagonal(self, p1, p2):
        p1, p2 = sorted([p1, p2])
        p1 = ("abcdefgh".index(p1[0]), int(p1[1]) - 1)
        p2 = ("abcdefgh".index(p2[0]), int(p2[1]) - 1)
        delta_x = p2[0] - p1[0]
        delta_y = p2[1] - p1[1]
        if not abs(delta_x) == abs(delta_y):
            return False
        delta_y = 1 if delta_y > 0 else -1
        positions = [p for lst in self.chess.values() for p in lst]
        for i in range(abs(delta_x) - 1):
            pos = "abcdefgh"[p1[0] + i + 1] + f"{p1[1] + 1 + delta_y * (i + 1)}"
            if pos in positions:
                return False
        return True

    def play(self, notation):
        if notation.castling:
            self.move(notation.fig, notation.castling[0][0], notation.castling[0][1])
            self.move(notation.next_fig, notation.castling[1][0], notation.castling[1][1])
            return
        if not notation.pos_from and not notation.castling:
            raise
        if notation.removed:
            self.remove(notation.removed)
        self.move(notation.fig, notation.pos_from, notation.pos_to)
        if notation.next_fig:
            self.remove(notation.pos_to)
            self.add(notation.next_fig, notation.pos_to)

    def __f(self, fig):
        fig_list = [0] * 64
        for j, color in enumerate("bw"):
            c = 2 * j - 1
            for i in [pos2num(pos) for pos in self.chess[color + fig]]:
                fig_list[i] = c
        return fig_list

    def is_clear_field(self, pos, ignore_color=None):
        chess = self.chess.items()
        if ignore_color:
            chess = [el for el in chess if not el[0][0] == ignore_color]
        return pos not in reduce(lambda a, b: a + b, [a for _, a in chess])

    def to_vector(self):
        return self.__f("p") + self.__f("r") + self.__f("n") + self.__f("b") + self.__f("q") + self.__f("k")

    def from_state(self, state):
        state = [state[i * 64:(i + 1) * 64] for i in range(6)]
        for k in self.chess.keys():
            self.chess[k] = []
        for n, fig in enumerate(["p", "r", "n", "b", "q", "k"]):
            for i, color in enumerate(state[n]):
                if color == 0:
                    continue
                if color < 0:
                    color = "b"
                else:
                    color = "w"
                self.chess[color + fig] += [num2pos(i)]
