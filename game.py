import torch
from board import Board
from utils import *
from functools import reduce
import ga

device = torch.device("cuda")


# noinspection PyShadowingNames
class Game:
    def __init__(self, model):
        self.model = model
        self.move_throw_attacked_field = None
        self.can_castling = (True, True)  # O-O, O-O-O
        self.board = None
        self.color = "w"
        self.opp_color = "b"

    def predict(self, board):
        self.board = board
        state = board.to_vector()
        cur = torch.tensor(state, dtype=torch.float).unsqueeze(0).to(device)
        with torch.no_grad():
            pos_from, pos_to = self.model(cur)
        matrix = pos_from.unsqueeze(1) * pos_to.unsqueeze(0)
        predicts = []
        for fig in self.board.chess.keys():
            if fig[0] == "b":
                for pos in self.board.chess[fig]:
                    next_positions = []
                    if fig == "bp":
                        next_positions = ga.black_pawn_move_variants(pos)
                        next_positions = self.filter_pawn_move(pos, next_positions)
                    elif fig == "br":
                        next_positions = ga.rook_move_variants(pos)
                        next_positions = self.filter_rook_move(pos, next_positions)
                    elif fig == "bn":
                        next_positions = ga.knight_move_variants(pos)
                        next_positions = self.filter_knight_move(next_positions)
                    elif fig == "bb":
                        next_positions = ga.bishop_move_variants(pos)
                        next_positions = self.filter_bishop_move(pos, next_positions)
                    elif fig == "bq":
                        next_positions = ga.queen_move_variants(pos)
                        next_positions = self.filter_queen_move(pos, next_positions)
                    elif fig == "bk":
                        next_positions = ga.king_move_variants(pos)
                        next_positions = self.filter_king_move(next_positions)
                    prob = [matrix[pos2num(pos), pos2num(next_pos)].item() for next_pos in next_positions]
                    next_positions = zip(next_positions, prob)
                    next_positions = list(
                        filter(lambda next_pos: not self.test_check(fig, pos, next_pos[0]), next_positions))
                    if next_positions:
                        predicts += [(fig, pos, *next_pos) for next_pos in next_positions]
        can_short, can_long = self.can_castling
        if can_short and self.board.is_clear_line("e8", "h8"):
            prob = matrix[pos2num("e8"), pos2num("g8")].item()
            predicts += [("O-O", None, None, prob)]
        if can_long and self.board.is_clear_line("e8", "a8"):
            prob = matrix[pos2num("e8"), pos2num("c8")].item()
            predicts += [("O-O-O", None, None, prob)]
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
                       [self.board.chess[k] for k in [k for k in self.board.chess.keys() if k[0] == self.color]])
        return list(filter(lambda pos: pos not in black, next_positions))

    def filter_pawn_move(self, cur_pos, next_positions):
        return list(filter(lambda next_pos: self.test_move_pawn(cur_pos, next_pos), next_positions))

    def filter_bishop_move(self, cur_pos, next_positions):
        return list(filter(
            lambda next_pos: self.board.is_clear_field(next_pos, self.opp_color) and self.board.is_clear_diagonal(cur_pos, next_pos), next_positions))

    def filter_rook_move(self, cur_pos, next_positions):
        return list(filter(
            lambda next_pos: self.board.is_clear_field(next_pos, self.opp_color) and self.board.is_clear_line(cur_pos, next_pos),
            next_positions))

    def filter_queen_move(self, cur_pos, next_positions):
        return self.filter_bishop_move(cur_pos, next_positions) + self.filter_rook_move(cur_pos, next_positions)

    def filter_king_move(self, next_positions):
        return list(filter(lambda next_pos: self.board.is_clear_field(next_pos, self.opp_color), next_positions))

    def test_check(self, fig, pos_from, pos):
        state = self.board.to_vector()
        self.board.remove(pos_from)
        self.board.remove(pos)
        self.board.chess[fig] += [pos]
        king_pos = self.board.chess[self.color+"k"][0]
        for pos in self.board.chess[self.opp_color+"p"]:
            if self.opp_color == "w":
                positions = ga.white_pawn_move_variants(pos)
            else:
                positions = ga.black_pawn_move_variants(pos)
            if king_pos in positions:
                self.board.from_state(state)
                return True
        for pos in self.board.chess[self.opp_color+"r"]:
            positions = ga.rook_move_variants(pos)
            if king_pos in positions and self.board.is_clear_line(king_pos, pos):
                self.board.from_state(state)
                return True
        for pos in self.board.chess[self.opp_color+"n"]:
            positions = ga.knight_move_variants(pos)
            if king_pos in positions:
                self.board.from_state(state)
                return True
        for pos in self.board.chess[self.opp_color+"b"]:
            positions = ga.bishop_move_variants(pos)
            if king_pos in positions and self.board.is_clear_diagonal(king_pos, pos):
                self.board.from_state(state)
                return True
        for pos in self.board.chess[self.opp_color+"q"]:
            positions = ga.queen_move_variants(pos)
            if king_pos in positions and (
                    self.board.is_clear_diagonal(king_pos, pos) or self.board.is_clear_line(king_pos, pos)):
                self.board.from_state(state)
                return True
        for pos in self.board.chess[self.opp_color+"k"]:
            positions = ga.king_move_variants(pos)
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
            return self.move_throw_attacked_field == pos_to or not self.board.is_clear_field(pos_to, self.color)

    def predict_next_pos(self, fig, cur_pos, cur_prob):
        positions = []
        for pos in self.predict_next_positions(fig, cur_pos):
            positions += [(pos, self.game_anal.board_out[pos2num(pos)])]
        if len(positions) == 0:
            return None, None, None, 0
        next_pos_prediction = min(positions, key=lambda a: a[1])
        next_pos, next_prob = next_pos_prediction[0], -next_pos_prediction[1]
        return fig, cur_pos, next_pos, cur_prob * next_prob
