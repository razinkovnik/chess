from notation import Notation
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from board import Board
from utils import translate_notation

from networks import SimpleLeaner
from game_analysis import *


class ChessCom:
    def __init__(self):
        self.driver = ChessCom.__init_driver()
        self.driver.get("https://www.chess.com/play/computer")
        self.driver.implicitly_wait(1)
        self.board = Board()
        model = SimpleLeaner()
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

    def update_board(self):
        self.board = Board()
        step_num = 0
        while True:
            try:
                color = step_num % 2
                move = self.driver.find_element_by_id(f"movelist_{step_num + 1}").text
                if move == "":
                    break
                move = translate_notation(move)
                self.__go(color, move)
            except NoSuchElementException:
                break
            step_num += 1
        self.board.show()

    def __go(self, color, move):
        return self.board.play(Notation(self.board, color, move))

    def __cell(self, pos):
        fig = self.driver.find_element_by_xpath("//*/img[@class='chess_com_piece chess_com_draggable']")
        size = fig.size['height']
        x = size * (8 - ("abcdefgh".index(pos[0]) + 1)) + size // 2
        y = size * int(pos[1]) - size // 2
        board_img = self.driver.find_element_by_id("chessboard_boardarea")
        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.move_to_element_with_offset(board_img, x, y)
        action.click()
        action.perform()

    def move(self, pos_from, pos_to):
        self.__cell(pos_from)
        self.__cell(pos_to)
        self.update_board()

    def predict_update(self):
        self.game.board = self.board
        next_move = self.game.predict()
        if not next_move:
            print("game end")
            return
        fig, pos_from, pos_to, prob = next_move
        if fig == "O-O":
            pos_from, pos_to = "e8", "g8"
        elif fig == "O-O-O":
            pos_from, pos_to = "e8", "c8"
        print(f"{fig} {pos_from}-{pos_to}, prob = {prob}")
        self.move(pos_from, pos_to)
        self.update_board()
