from utils import *


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
