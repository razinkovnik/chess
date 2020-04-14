from notation import Notation
from selenium import webdriver

from board import Board
from utils import translate_notation


class ChessCom:
    def __init__(self):
        self.driver = ChessCom.__init_driver()
        self.driver.get("https://www.chess.com/play/computer")
        self.driver.implicitly_wait(1)
        self.board = Board()
        self.step_num = 0

    @staticmethod
    def __init_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=C:\\Users\\m31k0l2\\AppData\\Local\\Google\\Chrome\\User Data")
        return webdriver.Chrome(options=options)

    def flip_board(self):
        flip_btn = self.driver.find_element_by_css_selector('*[title="Поменяться сторонами"]')
        flip_btn.click()

    def update_board(self):
        color = self.step_num % 2
        self.step_num += 1
        move = self.driver.find_element_by_id(f"movelist_{self.step_num}").text
        move = translate_notation(move)
        self.__go(color, move)

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
