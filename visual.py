from board import Board
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from utils import root_folder
import numpy as np

CELL_SIZE = 109


def setup_board():
    board = Image.new('RGBA', (CELL_SIZE * 8, CELL_SIZE * 8))
    draw = ImageDraw.Draw(board)
    black_color = "#769656"
    white_color = "#eeeed2"
    for j in range(1, 9):
        for i in range(1, 9):
            shape = [(CELL_SIZE * (i - 1), CELL_SIZE * (j - 1)), (CELL_SIZE * i, CELL_SIZE * j)]
            color = white_color if (i + j) % 2 == 0 else black_color
            draw.rectangle(shape, fill=color)
    figs = {}
    for fig in ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']:
        figs[fig] = Image.open(f'{root_folder}/{fig}.png', 'r').convert('RGBA')
    return board, figs


def paste_fig2pos(fig, pos, desk, figs):
    x, y = "abcdefgh".index(pos[0]), 8 - int(pos[1])
    desk.paste(figs[fig], (CELL_SIZE * x, CELL_SIZE * y), mask=figs[fig])


def show(board: Board):
    desk, figs = setup_board()
    for fig in board.chess.keys():
        for pos in board.chess[fig]:
            paste_fig2pos(fig, pos, desk, figs)
    fig, ax = plt.subplots()
    ax.imshow(np.asarray(desk))
    ax.set_title("ход")
    fig.set_figwidth(7)  # ширина и
    fig.set_figheight(7)  # высота "Figure"
    plt.show()
