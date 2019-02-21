"""
Neural Net for Chess Heuristic Function.
"""

import chess
import chess.pgn

pgn = open('datasets/ficsgamesdb_2018_CvC_nomovetimes_51973.pgn')
curr_parsed_game = chess.pgn.read_game(pgn)
i = 0
while curr_parsed_game is not None:
    curr_parsed_game = chess.pgn.read_game(pgn)
    i += 1
print(f"Parsed {i} games.")
# game2 = chess.pgn.read_game(pgn)
# board = game2.board()
# for i in game2.mainline_moves():
#     board.push(i)
#     print(board)
#     print("")