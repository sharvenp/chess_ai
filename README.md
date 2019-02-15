# chess_ai
Simple Neural Chess AI with MiniMax

Based on Matthia Sabatelli's Master Thesis on Neural Chess, this AI uses a standard MLP that takes in a board position and outputs an evaluation.

By using neural nets as function approximators, the MLP can be trained to approximate Stockfish's powerful evaluation function.

Stockfish is one of the most strongest chess engines out there that is also open source, but the drawback is that it requires a great deal of look-ahead to able to perform well. Hence this can be time consuming and by training an AI that can essentially do the same without any look-ahead, it makes the Neural AI output the same performace while taking less time. 

The evaluation value is essentially used to prune a serach tree of game states using the MiniMax algorithm coupled with Alpha-Beta pruning.

=== Dependencies ===
- python-chess
- keras
