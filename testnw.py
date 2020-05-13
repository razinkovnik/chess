from data import train_iter
from board import Board
from score import total_score
from game import Game
import ga
import asyncio
import time

batch = next(iter(train_iter))
inputs, targets = batch
n = 135
state = [int(x) for x in inputs[n].tolist()]
x, target = inputs[n].unsqueeze(0), targets[0].unsqueeze(0)
board = Board()
board.from_state(state)
board.show()


def get_half_steps(color, board, score_calc=False):
    game = Game(None)
    game.board = board
    game.color = color
    game.opp_color = "b" if color == "w" else "w"
    half_steps = []
    for fig in [color + fig for fig in ["p", "n", "b", "r", "q", "k"]]:
        start_positions = list(board.chess[fig])
        for start in start_positions:
            if fig[1] == "q":
                positions = ga.queen_move_variants(start)
                positions = game.filter_queen_move(start, positions)
            elif fig[1] == "r":
                positions = ga.rook_move_variants(start)
                positions = game.filter_rook_move(start, positions)
            elif fig[1] == "n":
                positions = ga.knight_move_variants(start)
                positions = game.filter_knight_move(positions)
            elif fig[1] == "b":
                positions = ga.bishop_move_variants(start)
                positions = game.filter_bishop_move(start, positions)
            elif fig[1] == "k":
                positions = ga.king_move_variants(start)
                positions = game.filter_king_move(positions)
            else:
                if fig == "bp":
                    positions = ga.black_pawn_move_variants(start)
                else:
                    positions = ga.white_pawn_move_variants(start)
                positions = game.filter_pawn_move(start, positions)
            positions = list(filter(lambda pos: not game.test_check(fig, start, pos), positions))
            if score_calc:
                half_steps += [([(start, end)], w - b) for end in positions for w, b in [total_score(board.clone().move(fig, start, end))]]
            else:
                half_steps += [([(start, end)]) for end in positions]
    if score_calc:
        return sorted(half_steps, key=lambda a: a[1])
    return half_steps


def get_next_moves(color, board, moves=None, score_calc=False):
    if moves is None:
        moves = get_half_steps(color, board, False)
        color = "w" if color == "b" else "b"
    moves = [get_next_moves_by_move(move, color, board, score_calc) for move in moves]
    return [step for move in moves for step in move]


async def get_next_moves_async(color, board, moves=None, score_calc=False):
    if moves is None:
        moves = get_half_steps(color, board, False)
        color = "w" if color == "b" else "b"
    results = await asyncio.gather(*[get_next_moves_by_move_coroutine(move, color, board, score_calc) for move in moves])
    return [move for moves in results for move in moves]


def get_next_moves_by_move(move, color, board, score_calc=False):
    next_moves = []
    next_board = board.clone()
    for (start, end) in move:
        fig = next_board.what_is(start)
        next_board = next_board.move(fig, start, end)
    opp = get_half_steps(color, next_board, score_calc)
    for opp_move in opp:
        if score_calc:
            next_moves += [(move + opp_move[0], opp_move[1])]
        else:
            next_moves += [move + opp_move]
    return next_moves


async def get_next_moves_by_move_coroutine(move, color, board, score_calc=False):
    return get_next_moves_by_move(move, color, board, score_calc)


async def main(color, board):
    moves = await get_next_moves_async(color, board, None, True)
    # moves = get_next_moves_async(color, board, moves, True)
    return moves


class Node:
    def __init__(self):
        self.start = None
        self.end = None
        self.score = 0
        self.board = None
        self.leaves = []


if __name__ == '__main__':
    node = Node()
    node.board = board
    moves = get_half_steps("b", board)