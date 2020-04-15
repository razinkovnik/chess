root_folder = 'C:\\Users\\m31k0l2\\Google Диск'


def pos2num(pos):
    c, r = "abcdefgh".index(pos[0]), int(pos[1]) - 1
    return r*8 + c


def num2pos(i):
    row = i // 8
    col = i - row*8
    return f"{'abcdefgh'[col]}{row+1}"


def translate_notation(move):
    move = move.replace('Кр', 'K')
    move = move.replace('Ф', 'Q')
    move = move.replace('Л', 'R')
    move = move.replace('С', 'B')
    return move.replace('К', 'N')
