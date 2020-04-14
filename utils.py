root_folder = 'C:\\Users\\m31k0l2\\Google Диск'


def pos2num(pos):
    c, r = "abcdefgh".index(pos[0]), int(pos[1]) - 1
    return r*8 + c


def num2pos(i):
    row = i // 8
    col = i - row*8
    return f"{'abcdefgh'[col]}{row+1}"


def translate_notation(enemy_move):
    if enemy_move[0] == "К":
        if enemy_move[1] == "р":
            return "K" + enemy_move[1:]
        return "N" + enemy_move[1:]
    if enemy_move[0] == "Ф":
        return "Q" + enemy_move[1:]
    if enemy_move[0] == "С":
        return "B" + enemy_move[1:]
    if enemy_move[0] == "С":
        return "B" + enemy_move[1:]
    if enemy_move[0] == "Л":
        return "R" + enemy_move[1:]
    return enemy_move
