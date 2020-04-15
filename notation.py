import re


class Notation:
    def __init__(self, board, color, move):
        self.color = color
        self.fig = None
        self.pos_from = None
        self.pos_to = None
        self.removed = None
        self.next_fig = None
        self.castling = None
        self.board = board
        self.__parse(move)

    def __castling(self, move):
        rook = "wb"[self.color] + "r"
        king = "wb"[self.color] + "k"
        k_pos = self.board.chess[king][0]
        if move == "O-O":
            self.castling = [(f"h{k_pos[1]}", f"f{k_pos[1]}"), (k_pos, f"g{k_pos[1]}")]
        else:
            self.castling = [(f"a{k_pos[1]}", f"d{k_pos[1]}"), (k_pos, f"c{k_pos[1]}")]
        self.fig, self.next_fig = rook, king

    def __parse(self, move):
        print(move)
        move = move.split("+")[0].split("#")[0]
        if 'O' in move:
            self.__castling(move)
            return
        match = re.match(
            '(?P<fig>[N|B|R|K|Q])?(?P<col>[a-h])?(?P<row>[1-8])?(?P<attack>x)?(?P<to>[a-h][1-8])(?P<nextfig>=[N|B|R|K|Q])?',
            move)
        fig, attack = match.group('fig'), match.group('attack')
        self.__pos_from_col = match.group('col')
        self.__pos_from_row = match.group('row')
        self.pos_to = match.group('to')
        self.fig = "wb"[self.color] + (fig.lower() if fig else "p")
        self.next_fig = match.group('nextfig')
        if self.next_fig:
            self.next_fig = self.fig[0] + self.next_fig[1].lower()
        if self.__pos_from_col and self.__pos_from_row:
            self.pos_from = self.__pos_from_col + self.__pos_from_row
            if attack:
                self.removed = self.pos_to
        elif "p" == self.fig[1]:
            self.__set4p(attack)
        elif self.__pos_from_col:
            self.pos_from = list(filter(lambda pos: pos[0] == self.__pos_from_col, self.board.chess[self.fig]))[0]
            if attack:
                self.removed = self.pos_to
        elif self.__pos_from_row:
            self.pos_from = list(filter(lambda pos: pos[1] == self.__pos_from_row, self.board.chess[self.fig]))[0]
            if attack:
                self.removed = self.pos_to
        elif "n" == self.fig[1]:
            self.__set4n(attack)
        elif "b" == self.fig[1]:
            self.__set4b(attack)
        elif "r" == self.fig[1]:
            self.__set4r(attack)
        elif "q" == self.fig[1]:
            self.__set4q(attack)
        elif "k" == self.fig[1]:
            self.__set4k(attack)

    def __set4k(self, attack):
        if attack:
            self.removed = self.pos_to
        self.pos_from = self.board.chess[self.fig][0]

    def __set4n(self, attack):
        if attack:
            self.removed = self.pos_to
        self.pos_from = self.board.find_knight_position(self.fig, self.pos_to)

    def __set4b(self, attack):
        if attack:
            self.removed = self.pos_to
        self.pos_from = self.board.find_bishop_position(self.fig, self.pos_to)

    def __set4r(self, attack):
        if attack:
            self.removed = self.pos_to
        self.pos_from = self.board.find_rook_position(self.fig, self.pos_to)

    def __set4q(self, attack):
        if attack:
            self.removed = self.pos_to
        self.pos_from = self.board.find_queen_position(self.fig, self.pos_to)

    def __set4p(self, attack):
        if attack:
            row = int(self.pos_to[1]) + [-1, 1][self.color]
            self.pos_from = f"{self.__pos_from_col}{row}"
            positions = [p for l in self.board.chess.values() for p in l]
            if self.pos_to not in positions:
                self.removed = self.pos_to[0] + f"{int(self.pos_to[1]) + [-1, 1][self.color]}"
            else:
                self.removed = self.pos_to
        else:
            self.pos_from = self.board.find_pawn_position(self.fig, self.pos_to)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.castling:
            return f"рокировка {'wb'[self.color]}: {self.castling[0]} - {self.castling[1]}"
        if self.removed:
            return f"атака {self.fig}: {self.pos_from}x{self.pos_to}"
        return f"ход {self.fig}: {self.pos_from}-{self.pos_to}"
