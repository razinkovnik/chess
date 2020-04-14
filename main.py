import time

from chess_com import ChessCom

chess = ChessCom()
time.sleep(3)
chess.flip_board()
chess.update_board()
chess.move("e7", "e5")
chess.update_board()
chess.board.show()
