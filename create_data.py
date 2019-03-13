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
import math

def get_bit_map(node):

    data_individual = [] 
    # White Pieces
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.PAWN, chess.WHITE))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.ROOK, chess.WHITE))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.KNIGHT, chess.WHITE))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.BISHOP, chess.WHITE))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.QUEEN, chess.WHITE))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.KING, chess.WHITE))).replace('', ' '), dtype=int, sep=' ').tolist())

    # Black Pieces
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.PAWN, chess.BLACK))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.ROOK, chess.BLACK))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.KNIGHT, chess.BLACK))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.BISHOP, chess.BLACK))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.QUEEN, chess.BLACK))).replace('', ' '), dtype=int, sep=' ').tolist())
    data_individual.extend(np.fromstring('{:064b}'.format(int(node.pieces(chess.KING, chess.BLACK))).replace('', ' '), dtype=int, sep=' ').tolist())

    return data_individual

def sigmoid(x):
    return 1/(1+(math.e**-x))

def main():

    engine = chess.engine.SimpleEngine.popen_uci("stockfish10/Windows/stockfish_10_x64.exe")
    X = []
    Y = []
    pgn = open("datasets/ficsgamesdb_2018_CvC_nomovetimes_51973.pgn")
    state_limit = 60
    games = 300
    evaluation_time = 1
    start = time.time()

    print(f"Parsing {games} games.")

    for i in range(games):

        game = chess.pgn.read_game(pgn)
        board = game.board()
        states = 0
        print("Game:", i+1, f"({game.headers['Event']})")

        for next_node in game.mainline_moves(): 
            
            evaluation = engine.analyse(board, chess.engine.Limit(time=evaluation_time))
            score = sigmoid((2*int(board.turn) -1) * (evaluation['score'].relative.score(mate_score=1000000)))
            X.append(get_bit_map(board))
            Y.append(score)
            states += 1

            board.push(next_node)

            if states >= state_limit:
                break

        end = time.time()
        print("States:", states)
        hours, rem = divmod(end-start, 3600)
        minutes, seconds = divmod(rem, 60)
        print(f"Time Elapsed:", "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    engine.quit()

    print("Dataset created")
    print("Samples:", len(X), "Labels:", len(Y))
    print("Dumping to JSON")

    with open('data.json', 'w') as outfile:
        json.dump([X,Y], outfile)

if __name__ == "__main__":
    main()