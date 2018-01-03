import random
import os
import chess.pgn

from animations.base import BaseBeamAnim, check_interrupt, adjustable
from beam.state import beam_state

PIXELS_PER_STRIP = int(os.environ.get('PIXELS_PER_STRIP', "60"))

colors = ['#ff0000', '#00ff00', '#0000ff']


class Chess(BaseBeamAnim):

    def __init__(self, layout, dir=True):
        super().__init__(layout)

        self.colors = beam_state.colors

        # Load chess game
        pgn = open('test.pgn')
        self.game = chess.pgn.read_game(pgn)
        self.board = self.game.board()

        self.moves = list(self.game.main_line())
        self.cur_move = 0

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        self.layout.all_off()

        pieces = self.board.piece_map()

        for square in pieces:
            x = square % PIXELS_PER_STRIP
            y = int(square / PIXELS_PER_STRIP)
            piece_type = pieces[square].symbol()

            self.layout.set(x, y, random.choice(self.colors))

        self.cur_move += 1
        if self.cur_move >= len(self.moves):
            self.cur_move = 0
            self.board.reset()
        else:
            self.board.push(self.moves[self.cur_move])

        self._step += amt
