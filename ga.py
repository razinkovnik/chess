from utils import *
from functools import reduce


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


def white_pawn_move_variants(pos):
    pos_num = pos2num(pos)
    positions = [num2pos(pos_num + 8)]
    if pos_num % 8 > 0:
        positions += [num2pos(pos_num + 7)]
    if not pos_num % 8 == 7:
        positions += [num2pos(pos_num + 9)]
    if pos2num("a2") <= pos_num <= pos2num("h2"):
        positions += [num2pos(pos_num + 16)]
    return positions


# def white_pawn_attack_variants(pos):
#     pos_num = pos2num(pos)
#     # positions = [num2pos(pos_num+8)]
#     positions = []
#     if pos_num % 8 > 0:
#         positions += [num2pos(pos_num + 7)]
#     if not pos_num % 8 == 7:
#         positions += [num2pos(pos_num + 9)]
#     # if pos2num("a2") <= pos_num <= pos2num("h2"):
#     #     positions += [num2pos(pos_num+16)]
#     return positions


def rook_move_variants(pos):
    pos = pos2num(pos)
    row = pos // 8
    col = pos % 8
    return [num2pos(n) for n in
            [i + row * 8 for i in range(8) if not i == col] + [col + i * 8 for i in range(8) if not i == row]]


def bishop_move_variants(pos):
    pos = pos2num(pos)
    positions = []

    next_pos = pos - 7
    if pos % 8 < 7:
        for _ in range(pos // 8):
            if next_pos < 0:
                break
            positions += [num2pos(next_pos)]
            if next_pos % 8 == 7:
                break
            next_pos = next_pos - 7

    next_pos = pos + 7
    if pos % 8 > 0:
        for _ in range(8 - pos // 8):
            if next_pos > 63:
                break
            positions += [num2pos(next_pos)]
            if next_pos % 8 == 0:
                break
            next_pos = next_pos + 7

    next_pos = pos - 9
    if pos % 8 > 0:
        for _ in range(pos // 8):
            if next_pos < 0:
                break
            positions += [num2pos(next_pos)]
            if next_pos % 8 == 0:
                break
            next_pos = next_pos - 9

    next_pos = pos + 9
    if pos % 8 < 7:
        for _ in range(8 - pos // 8):
            if next_pos > 63:
                break
            positions += [num2pos(next_pos)]
            if next_pos % 8 == 7:
                break
            next_pos = next_pos + 9

    return positions


def queen_move_variants(pos):
    return bishop_move_variants(pos) + rook_move_variants(pos)


def king_move_variants(pos):
    pos = pos2num(pos)
    return [num2pos(p) for p in [pos - 1, pos + 1, pos - 8, pos + 8, pos - 7, pos + 9, pos + 7, pos - 9] if
            64 > p >= 0 and abs(p % 8 - pos % 8) <= 1]


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


def opp_color(color):
    return "w" if color is "b" else "b"


def filter_knight_move(board, color, next_positions):
    black = reduce(lambda a, b: a + b,
                   [board.chess[k] for k in [k for k in board.chess.keys() if k[0] == color]])
    return list(filter(lambda pos: pos not in black, next_positions))


def filter_pawn_move(board, color, cur_pos, next_positions, move_throw_attacked_field=None):
    return list(filter(lambda next_pos: test_move_pawn(board, color, cur_pos, next_pos, move_throw_attacked_field), next_positions))


def filter_bishop_move(board, color, cur_pos, next_positions):
    return list(filter(
        lambda next_pos: board.is_clear_field(next_pos, opp_color(color)) and board.is_clear_diagonal(cur_pos, next_pos), next_positions))


def filter_rook_move(board, color, cur_pos, next_positions):
    return list(filter(
        lambda next_pos: board.is_clear_field(next_pos, opp_color(color)) and board.is_clear_line(cur_pos, next_pos),
        next_positions))


def filter_queen_move(board, color, cur_pos, next_positions):
    return filter_bishop_move(board, color, cur_pos, next_positions) + filter_rook_move(board, color, cur_pos, next_positions)


def filter_king_move(board, color, next_positions):
    return list(filter(lambda next_pos: board.is_clear_field(next_pos, opp_color(color)), next_positions))


def test_move_pawn(board, color, pos_from, pos_to, move_throw_attacked_field=None):
    if pos_from[0] == pos_to[0]:
        return board.is_clear_field(pos_to)
    if int(pos_from[1]) - int(pos_from[1]) == 2:
        next_field = f"{pos_from[0]}{int(pos_from[1]) + 1}"
        return board.is_clear_field(next_field)
    else:
        return move_throw_attacked_field == pos_to or not board.is_clear_field(pos_to, color)


def test_check(board, color, fig, pos_from, pos):
    board = board.clone()
    opp = opp_color(color)
    board.remove(pos_from)
    board.remove(pos)
    board.chess[fig] += [pos]
    king_pos = board.chess[color+"k"][0]
    for pos in board.chess[opp+"p"]:
        positions = white_pawn_move_variants(pos) if opp == "w" else black_pawn_move_variants(pos)
        if king_pos in positions:
            return True
    for pos in board.chess[opp+"r"]:
        positions = rook_move_variants(pos)
        if king_pos in positions and board.is_clear_line(king_pos, pos):
            return True
    for pos in board.chess[opp+"n"]:
        positions = knight_move_variants(pos)
        if king_pos in positions:
            return True
    for pos in board.chess[opp+"b"]:
        positions = bishop_move_variants(pos)
        if king_pos in positions and board.is_clear_diagonal(king_pos, pos):
            return True
    for pos in board.chess[opp+"q"]:
        positions = queen_move_variants(pos)
        if king_pos in positions and (
                board.is_clear_diagonal(king_pos, pos) or board.is_clear_line(king_pos, pos)):
            return True
    for pos in board.chess[opp+"k"]:
        positions = king_move_variants(pos)
        if king_pos in positions:
            return True
    return False
