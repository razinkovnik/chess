from board import Board
from utils import *
import numpy as np
import ga


def material_score(color, board):
    return sum(
        [len(board.chess[color + fig]) * value for fig, value in zip(["p", "n", "b", "r", "q"], [1, 3, 3, 5, 9])])


def king_side_score(color, board):
    king = board.chess[color + "k"][0]
    rooks = board.chess[color + "r"]
    row_1 = "1" if color == "w" else "8"
    row_2 = "2" if color == "w" else "7"
    row_3 = "3" if color == "w" else "6"
    score = 0
    if king not in ["b" + row_1, "c" + row_1, "g" + row_1] or king == "g" + row_1 \
            and "h" + row_1 in rooks or king in ["b" + row_1, "c" + row_1] and "a" + row_1 in rooks \
            or king in ["b" + row_1, "c" + row_1] and "b" + row_1:
        score -= 0.5
    else:
        if king[0] == "c":
            score -= 0.25
        pawns = board.chess[color + "p"]
        if king[0] == "g":
            for col in ["f", "g", "h"]:
                if col + row_2 not in pawns:
                    score -= 0.25
                    if col + row_3 not in pawns:
                        score -= 0.25
        else:
            for col in ["a", "b", "c"]:
                if col + row_2 not in pawns:
                    score -= 0.25
                    if col + row_3 not in pawns:
                        score -= 0.25
    return score


def center_score(color, board):
    positions = {a for k, v in board.chess.items() for a in v if k[0] == color}
    main_center = {"d4", "d5", "e4", "e5"}
    side_center = {"c3", "c4", "c5", "c6", "d3", "d6", "e3", "e6", "f3", "f4", "f5", "f6"}
    return len(positions.intersection(main_center)) * 0.5 + len(positions.intersection(side_center)) * 0.25


def open_line_score(color, board):
    positions = [board.chess[fig] for fig in [color + "r", color + "b", color + "q"]]
    positions = [pos for x in positions for pos in x]
    return sum([__open_line_score(pos, board) for pos in positions])


def __open_line_score(pos, board, dir=""):
    if dir == "":
        fig = board.what_is(pos)
        sign = 1 if fig[0] == "w" else -1
        if fig[1] in "bq":
            dir += "d"
        if fig[1] in "rq":
            dir += "v"
            if fig[0] == "w" and pos[1] in ["7", "8"] or fig[0] == "b" and pos[1] in ["1", "2"]:
                dir += "h"
        return sign * __open_line_score(pos, board, dir)
    pawns = board.chess["wp"] + board.chess["bp"]
    score = 0.0
    if "v" in dir and pos[0] not in [p[0] for p in pawns]:
        score += 0.5 if pos[0] in ("d", "e") else 0.25
    if "h" in dir and pos[1] not in [p[1] for p in pawns]:
        score += 0.5
    if "d" in dir:
        diag1 = {"a1", "b2", "c3", "d4", "e5", "f6", "g7", "h8"}
        diag2 = {"a8", "b7", "c6", "d5", "e4", "f3", "g2", "h1"}
        if pos in diag1 and len(diag1.intersection(pawns)) == 0:
            score += 0.5
        elif pos in diag2 and len(diag2.intersection(pawns)) == 0:
            score += 0.5
    return score


def __strong_field_score(pos, board):
    score = False
    pawns = board.chess["wp" if pos < 32 else "bp"]
    king = board.chess["wk" if pos < 32 else "bk"][0]
    if pos % 8 < 7:
        score = score or num2pos(pos + (-7 if pos < 32 else 9)) in pawns
    if pos % 8 > 0:
        score = score or num2pos(pos + (-9 if pos < 32 else 7)) in pawns
    if score:
        king = pos2num(king) % 8
        if pos in [27, 28, 35, 36] or pos % 8 in [p for p in [king - 1, king, king + 1] if -1 < p < 8]:
            return 0.5
        return 0.25
    return 0


def strong_field_score(color, board):
    start, end = ("a3", "a5") if color == "w" else ("a5", "a7")
    positions = range(pos2num(start), pos2num(end))
    return sum([__strong_field_score(pos, board) for pos in positions])


def chain_score(color, board):
    # пешечная цепь
    pawns = sorted(board.chess[color + "p"])
    pawns = [pos2num(p) for p in pawns]
    cols = [p % 8 for p in pawns]
    raws = [p // 8 for p in pawns]
    # изолированные
    delta = np.array(cols[1:]) - np.array(cols[:-1])
    isolated_pawns = len(delta[delta > 1]) * -0.25
    # сдвоенные
    dual_pawns = (len(cols) - len(set(cols))) * -0.25
    # отстающие
    left_shifted = (np.array(raws[:-1]) - np.array(raws[1:])).tolist()
    right_shifted = (np.array(raws[1:]) - np.array(raws[:-1])).tolist()
    behind_pawns = len(list(filter(lambda a: a < 0, left_shifted + right_shifted))) * -0.25
    # на последней линии
    last_line_pawns = len([r for r in raws if r == (6 if color == "w" else 1)]) * 0.5
    return isolated_pawns + dual_pawns + behind_pawns + last_line_pawns


def move_count(board, color, fig):
    move_count = 0
    for pos in board.chess[color + fig]:
        moves = []
        if fig == "q":
            moves += ga.filter_queen_move(board, color, pos, ga.queen_move_variants(pos))
        elif fig == "r":
            moves += ga.filter_rook_move(board, color, pos, ga.rook_move_variants(pos))
        elif fig == "b":
            moves += ga.filter_bishop_move(board, color, pos, ga.bishop_move_variants(pos))
        elif fig == "n":
            moves += ga.filter_knight_move(board, color, ga.knight_move_variants(pos))
        move_count += sum([0 if ga.test_check(board, color, color + fig, pos, move) else 1 for move in moves])
    return move_count


def check_pawns_score(color, board):
    pawns = sorted(board.chess[color + "p"])
    flank = lambda king: ["a", "b"] if pos2num(king) % 8 > 4 else ["g", "h"]
    center = lambda king: ["c", "d"] if pos2num(king) % 8 > 4 else ["e", "g"]
    king = board.chess[color + "k"][0]
    pawns_flank = [pos2num(p) for p in pawns if p[0] in flank(king)]
    pawns_center = [pos2num(p) for p in pawns if p[0] in center(king)]
    check_pawns = lambda rows: (len(rows.intersection([row - 1, row, row + 1])) for row in rows)
    count_check_pawns = lambda pawns: len([p for p in check_pawns({p % 8 for p in pawns}) if p == 0])
    return count_check_pawns(pawns_flank) * 0.5 + count_check_pawns(pawns_center) * 0.25


def active_fig_score(color, board):
    return sum([move_count(board, color, fig) for fig in ["q", "r", "b", "n"]]) * 0.1


def total_score(board):
    scores = [[material_score(color, board),
               king_side_score(color, board),
               center_score(color, board),
               open_line_score(color, board),
               strong_field_score(color, board),
               chain_score(color, board),
               check_pawns_score(color, board),
               active_fig_score(color, board)] for color in ["w", "b"]]
    # print(scores)
    return [sum(scores[0]), sum(scores[1])]
