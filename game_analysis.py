import torch
from board import Board
from utils import *
from functools import reduce

device = torch.device("cuda")


class GameAnalysis:
    def __init__(self, model):
        self.model = model
        self.cur_positions = {}
        self.next_positions = {}
        self.board_out = None

    def board(self, cur):
        figs = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        for i, fig in enumerate(figs):
            lst = cur[i * 64:(i + 1) * 64].tolist()
            self.cur_positions[fig] = [num2pos(i) for i, x in enumerate(lst) if x < 0]

        self.board_out = self.model(cur.unsqueeze(0)).tolist()
        for i, fig in enumerate(figs):
            lst = self.board_out[i * 64:(i + 1) * 64]
            self.next_positions[fig] = {}
            for pos in self.cur_positions[fig]:
                self.next_positions[fig][pos] = 1 + lst[pos2num(pos)]

    def top_n(self, n):
        min_prob = min(sorted(
            list(reduce(lambda a, b: a + b, [list(positions.values()) for positions in self.next_positions.values()])),
            reverse=True)[:n])
        filtered_positions = {}
        for k in self.next_positions.keys():
            positions = self.next_positions[k]
            filtered = list(filter(lambda a: a[1] >= min_prob, positions.items()))
            if len(filtered) > 0:
                filtered_positions[k] = dict(filtered)
        return filtered_positions

    def what_is(self, pos):
        for k in self.cur_positions.keys():
            if pos in self.cur_positions[k]:
                return k

    @staticmethod
    def black_pawn_move_variants(pos):
        pos_num = pos2num(pos)
        positions = [num2pos(pos_num - 8)]
        if pos_num % 8 > 0:
            positions += [num2pos(pos_num - 9)]
        if not pos_num % 8 == 7:
            positions += [num2pos(pos_num - 7)]
        if pos2num("a7") <= pos_num <= pos2num("h7"):
            positions += [num2pos(pos_num - 16)]
        return positions

    @staticmethod
    def white_pawn_attack_variants(pos):
        pos_num = pos2num(pos)
        # positions = [num2pos(pos_num+8)]
        positions = []
        if pos_num % 8 > 0:
            positions += [num2pos(pos_num + 7)]
        if not pos_num % 8 == 7:
            positions += [num2pos(pos_num + 9)]
        # if pos2num("a2") <= pos_num <= pos2num("h2"):
        #     positions += [num2pos(pos_num+16)]
        return positions

    @staticmethod
    def rook_move_variants(pos):
        pos = pos2num(pos)
        row = pos // 8
        col = pos % 8
        return [num2pos(n) for n in
                [i + row * 8 for i in range(8) if not i == col] + [col + i * 8 for i in range(8) if not i == row]]

    @staticmethod
    def bishop_move_variants(pos):
        pos = pos2num(pos)
        positions = []

        next_pos = pos - 7
        if pos % 8 < 7 and next_pos >= 0:
            for _ in range(pos // 8):
                positions += [num2pos(next_pos)]
                if next_pos % 8 == 7:
                    break
                next_pos = next_pos - 7

        next_pos = pos + 7
        if pos % 8 > 0 and next_pos < 64:
            for _ in range(8 - pos // 8):
                positions += [num2pos(next_pos)]
                if next_pos % 8 == 0:
                    break
                next_pos = next_pos + 7

        next_pos = pos - 9
        if pos % 8 > 0 and next_pos >= 0:
            for _ in range(pos // 8):
                positions += [num2pos(next_pos)]
                if next_pos % 8 == 0:
                    break
                next_pos = next_pos - 9

        next_pos = pos + 9
        if pos % 8 < 7 and next_pos < 64:
            for _ in range(8 - pos // 8):
                positions += [num2pos(next_pos)]
                if next_pos % 8 == 7:
                    break
                next_pos = next_pos + 9

        return positions

    def queen_move_variants(self, pos):
        return self.bishop_move_variants(pos) + self.rook_move_variants(pos)

    @staticmethod
    def king_move_variants(pos):
        pos = pos2num(pos)
        return [num2pos(p) for p in [pos - 1, pos + 1, pos - 8, pos + 8, pos - 7, pos + 9, pos + 7, pos - 9] if
                64 > p >= 0 and abs(p % 8 - pos % 8) <= 1]

    @staticmethod
    def knight_move_variants(pos):
        cur_pos = pos2num(pos)
        left1 = cur_pos % 8 >= 1
        left2 = cur_pos % 8 >= 2
        right1 = 8 - cur_pos % 8 > 1
        right2 = 8 - cur_pos % 8 > 2
        bottom1 = cur_pos // 8 >= 1
        bottom2 = cur_pos // 8 >= 2
        top1 = 8 - cur_pos // 8 > 1
        top2 = 8 - cur_pos // 8 > 2

        positions = []
        if left1 and top2:
            positions += [num2pos(cur_pos + 16 - 1)]
        if right1 and top2:
            positions += [num2pos(cur_pos + 16 + 1)]
        if left1 and bottom2:
            positions += [num2pos(cur_pos - 16 - 1)]
        if right1 and bottom2:
            positions += [num2pos(cur_pos - 16 + 1)]
        if left2 and top1:
            positions += [num2pos(cur_pos + 8 - 2)]
        if right2 and top1:
            positions += [num2pos(cur_pos + 8 + 2)]
        if left2 and bottom1:
            positions += [num2pos(cur_pos - 8 - 2)]
        if right2 and bottom1:
            positions += [num2pos(cur_pos - 8 + 2)]
        return positions


# noinspection PyShadowingNames
class Game:
    def __init__(self, model):
        self.game_anal = GameAnalysis(model)
        self.board = Board()
        self.figs = {
            "pawn": "bp",
            "knight": "bn",
            "bishop": "bb",
            "rook": "br",
            "queen": "bq",
            "king": "bk"
        }
        self.move_throw_attacked_field = None
        self.can_castling = (True, True)  # O-O, O-O-O

    def predict(self):
        state = self.board.to_vector()
        return self.predict_from_state(state)

    def predict_from_state(self, cur_state, top_n=16):
        cur = torch.tensor(cur_state, dtype=torch.float).to(device)
        self.board.from_state(cur_state)
        self.game_anal.board(cur)
        tops = self.game_anal.top_n(top_n)
        predicts = []
        for fig in tops.keys():
            for cur_pos in tops[fig]:
                cur_prob = tops[fig][cur_pos]
                predicts += [self.predict_next_pos(fig, cur_pos, cur_prob)]
        short_castling, long_castling = self.predict_castling()
        if short_castling:
            predicts += [("O-O", None, None, short_castling)]
        if long_castling:
            predicts += [("O-O-O", None, None, long_castling)]
        predicts = list(filter(lambda a: a[0], predicts))
        if len(list(predicts)) == 0:
            return None
        return max(predicts, key=lambda a: a[3])

    # noinspection PyGlobalUndefined
    def predict_castling(self):
        global king_probs
        can_short, can_long = self.can_castling
        short_castling, long_castling = None, None
        if can_short or can_long:
            out = self.game_anal.board_out
            king_probs = out[-64:]
        if can_short and self.board.is_clear_line("e8", "h8"):
            short_castling = -king_probs[pos2num("g8")] * (1 + king_probs[pos2num("e8")])
        if can_long and self.board.is_clear_line("e8", "a8"):
            long_castling = -king_probs[pos2num("c8")] * (1 + king_probs[pos2num("e8")])
        return short_castling, long_castling

    def filter_knight_move(self, next_positions):
        black = reduce(lambda a, b: a + b,
                       [self.board.chess[k] for k in [k for k in self.board.chess.keys() if k[0] == 'b']])
        return list(filter(lambda pos: pos not in black, next_positions))

    def filter_pawn_move(self, cur_pos, next_positions):
        return list(filter(lambda next_pos: self.test_move_pawn(cur_pos, next_pos), next_positions))

    def filter_bishop_move(self, cur_pos, next_positions):
        return list(filter(
            lambda next_pos: self.board.is_clear_field(next_pos, "w") and self.board.is_clear_diagonal(cur_pos,
                                                                                                       next_pos),
            next_positions))

    def filter_rook_move(self, cur_pos, next_positions):
        return list(filter(
            lambda next_pos: self.board.is_clear_field(next_pos, "w") and self.board.is_clear_line(cur_pos, next_pos),
            next_positions))

    def filter_queen_move(self, cur_pos, next_positions):
        return self.filter_bishop_move(cur_pos, next_positions) + self.filter_rook_move(cur_pos, next_positions)

    def filter_king_move(self, next_positions):
        return list(filter(lambda next_pos: self.board.is_clear_field(next_pos, "w"), next_positions))

    def test_check(self, fig, pos_from, pos):
        state = self.board.to_vector()
        self.board.remove(pos_from)
        self.board.remove(pos)
        self.board.chess[fig] += [pos]
        king_pos = self.board.chess["bk"][0]
        for pos in self.board.chess["wp"]:
            positions = self.game_anal.white_pawn_attack_variants(pos)
            if king_pos in positions:
                self.board.from_state(state)
                return True
        for pos in self.board.chess["wr"]:
            positions = self.game_anal.rook_move_variants(pos)
            if king_pos in positions and self.board.is_clear_line(king_pos, pos):
                self.board.from_state(state)
                return True
        for pos in self.board.chess["wn"]:
            positions = self.game_anal.knight_move_variants(pos)
            if king_pos in positions:
                self.board.from_state(state)
                return True
        for pos in self.board.chess["wb"]:
            positions = self.game_anal.bishop_move_variants(pos)
            if king_pos in positions and self.board.is_clear_diagonal(king_pos, pos):
                self.board.from_state(state)
                return True
        for pos in self.board.chess["wq"]:
            positions = self.game_anal.queen_move_variants(pos)
            if king_pos in positions and (
                    self.board.is_clear_diagonal(king_pos, pos) or self.board.is_clear_line(king_pos, pos)):
                self.board.from_state(state)
                return True
        for pos in self.board.chess["wk"]:
            positions = self.game_anal.king_move_variants(pos)
            if king_pos in positions:
                self.board.from_state(state)
                return True
        self.board.from_state(state)
        return False

    def test_move_pawn(self, pos_from, pos_to):
        if pos_from[0] == pos_to[0]:
            return self.board.is_clear_field(pos_to)
        if int(pos_from[1]) - int(pos_from[1]) == 2:
            next_field = f"{pos_from[0]}{int(pos_from[1]) + 1}"
            return self.board.is_clear_field(next_field)
        else:
            return self.move_throw_attacked_field == pos_to or not self.board.is_clear_field(pos_to, "b")

    def predict_next_positions(self, fig, cur_pos):
        global next_positions
        if fig == "pawn":
            next_positions = self.game_anal.black_pawn_move_variants(cur_pos)
            next_positions = self.filter_pawn_move(cur_pos, next_positions)
        elif fig == "rook":
            next_positions = self.game_anal.rook_move_variants(cur_pos)
            next_positions = self.filter_rook_move(cur_pos, next_positions)
        elif fig == "knight":
            next_positions = self.game_anal.knight_move_variants(cur_pos)
            next_positions = self.filter_knight_move(next_positions)
        elif fig == "bishop":
            next_positions = self.game_anal.bishop_move_variants(cur_pos)
            next_positions = self.filter_bishop_move(cur_pos, next_positions)
        elif fig == "queen":
            next_positions = self.game_anal.queen_move_variants(cur_pos)
            next_positions = self.filter_queen_move(cur_pos, next_positions)
        elif fig == "king":
            next_positions = self.game_anal.king_move_variants(cur_pos)
            next_positions = self.filter_king_move(next_positions)
        next_positions = filter(lambda next_pos: not self.test_check(self.figs[fig], cur_pos, next_pos), next_positions)
        return next_positions

    def predict_next_pos(self, fig, cur_pos, cur_prob):
        positions = []
        for pos in self.predict_next_positions(fig, cur_pos):
            positions += [(pos, self.game_anal.board_out[pos2num(pos)])]
        if len(positions) == 0:
            return None, None, None, 0
        next_pos_prediction = min(positions, key=lambda a: a[1])
        next_pos, next_prob = next_pos_prediction[0], -next_pos_prediction[1]
        return fig, cur_pos, next_pos, cur_prob * next_prob

    def show(self):
        next_move = self.predict()
        if not next_move:
            print("game end")
            self.board.show()
            return
        fig, pos_from, pos_to, prob = next_move
        if fig in ["O-O", "O-O-O"]:
            self.board.play(Notation(self.board, 1, fig))
            print(f"{fig}, prob = {prob}")
        else:
            fig = self.figs[fig]
            if not self.board.is_clear_field(pos_to):
                self.board.remove(pos_to)
            self.board.move(fig, pos_from, pos_to)
            print(f"{fig} {pos_from}-{pos_to}, prob = {prob}")
        self.board.show()
