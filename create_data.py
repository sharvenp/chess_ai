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
import random 

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

def main():

    engine = chess.engine.SimpleEngine.popen_uci("stockfish10/Windows/stockfish_10_x64.exe")
    output_data = []
    pgn = open("datasets/ficsgamesdb_2018_CvC_nomovetimes_51973.pgn")
    state_limit = 30
    games = 600
    evaluation_time = 1
    start = time.time()

    print(f"Parsing {games} games.")

    for i in range(games):

        node = chess.pgn.read_game(pgn)
        states = 0
        print("Game:", i+1, "(", node.headers["Event"] ,")")

        while node.variations and states < state_limit: 
            
            next_node = node.variation(random.randint(0, len(node.variations)-1))
            evaluation = engine.analyse(next_node.board(), chess.engine.Limit(time=evaluation_time))
            score = (2*int(next_node.board().turn) -1) * (evaluation['score'].relative.score(mate_score=1000000))/100.0
            output_data.append((get_bit_map(next_node.board()), score))
            node = next_node
            states += 1

        end = time.time()
        print("States:", states)
        print(f"Time Elapsed: {end-start}")

    engine.quit()
    print("Dataset created")
    print("Size:", len(output_data))
    print("Dumping to JSON")

    with open('data.json', 'w') as outfile:
        json.dump(output_data, outfile)

if __name__ == "__main__":
    main()