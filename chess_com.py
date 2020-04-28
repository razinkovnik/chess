import time
import re

from notation import Notation
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from board import Board
from utils import translate_notation

from networks import SimpleLinear, SimpleConv2d, ConvEncoderDecoder
from game_analysis import *


class ChessCom:
    def __init__(self):
        self.driver = ChessCom.__init_driver()
        self.driver.get("https://www.chess.com/play/computer")
        self.driver.implicitly_wait(1)
        self.board = Board()
        # model = SimpleLeaner()
        model = ConvEncoderDecoder()
        model.load()
        self.game = Game(model)

    @staticmethod
    def __init_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=C:\\Users\\m31k0l2\\AppData\\Local\\Google\\Chrome\\User Data")
        return webdriver.Chrome(options=options)

    def flip_board(self):
        flip_btn = self.driver.find_element_by_css_selector('*[title="Поменяться сторонами"]')
        flip_btn.click()

    def read_moves(self):
        move_list = self.driver.find_element_by_id("moveListControl_vertical")
        while True:
            try:
                moves = move_list.find_elements_by_tag_name("span")
                moves = [move.text for move in moves]
                break
            except StaleElementReferenceException:
                pass
        return [translate_notation(move) for move in moves if re.match(r".*[a-zO]", move)]

    def update_board(self, moves):
        self.board = Board()
        for step_num, move in enumerate(moves):
            self.__go(step_num % 2, move)
        self.game.board = self.board

    def __go(self, color, move):
        return self.board.play(Notation(self.board, color, move))

    def __cell(self, pos):
        board_img = self.driver.find_element_by_id("chessboard_boardarea")
        size = board_img.size["height"] // 8
        x = size * (8 - ("abcdefgh".index(pos[0]) + 1)) + size // 2
        y = size * int(pos[1]) - size // 2

        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.move_to_element_with_offset(board_img, x, y)
        action.click()
        action.perform()

    def move(self, pos_from, pos_to):
        self.__cell(pos_from)
        self.__cell(pos_to)

    # def predict_update(self):
    #     self.game.board = self.board
    #     next_move = self.game.predict()
    #     if not next_move:
    #         print("game end")
    #         return
    #     fig, pos_from, pos_to, prob = next_move
    #     if fig == "O-O":
    #         pos_from, pos_to = "e8", "g8"
    #     elif fig == "O-O-O":
    #         pos_from, pos_to = "e8", "c8"
    #     print(f"{fig} {pos_from}-{pos_to}, prob = {prob}")
    #     self.move(pos_from, pos_to)
    #     time.sleep(1)
    #     self.update_board()

