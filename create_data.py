"""
Creates the dataset for the MLP in .json format.
.json file will contain board-value pairs. 

Vectorize the SquareSet integer mask of the piece
"""
import json
import chess.pgn
import chess.engine
import time
import numpy as np

data_individual = []

engine = chess.engine.SimpleEngine.popen_uci("stockfish10/Windows/stockfish_10_x64.exe")
game = chess.pgn.read_game(open("datasets/ficsgamesdb_2018_CvC_nomovetimes_51973.pgn"))
node = game 
final_bit_map = []
output_data = []

while node.variations: 
    
    next_node = node.variation(0)

    evaluation = engine.analyse(next_node.board(), chess.engine.Limit(time=1))
    score = (2*int(next_node.board().turn) -1) * (evaluation['score'].relative.score(mate_score=1000000))/100.0
    print(score, "\n", next_node.board())

    # data_individual = [] 
    # final_bit_map = []

    # # White Pieces
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.PAWN, chess.WHITE))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.ROOK, chess.WHITE))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.KNIGHT, chess.WHITE))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.BISHOP, chess.WHITE))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.QUEEN, chess.WHITE))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.KING, chess.WHITE))).replace('', ' '), dtype=int, sep=' '))

    # # Black Pieces
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.PAWN, chess.BLACK))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.ROOK, chess.BLACK))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.KNIGHT, chess.BLACK))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.BISHOP, chess.BLACK))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.QUEEN, chess.BLACK))).replace('', ' '), dtype=int, sep=' '))
    # data_individual.append(np.fromstring('{:064b}'.format(int(node.board().pieces(chess.KING, chess.BLACK))).replace('', ' '), dtype=int, sep=' '))

    # for bit_map in data_individual:
    #     final_bit_map = np.append(final_bit_map, bit_map)

    # output_data.append(final_bit_map)

    node = next_node

engine.quit()
print("Dataset created.")