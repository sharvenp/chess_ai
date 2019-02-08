"""
chess.py : A simple Chess framework implemented in python.
Created On: 27 Jan 2019
Author: Sharven

Classes:
    - State -> Represents a state of a board. 
        - board : numpy.ndarray
        - value : float (maybe int)
    - Piece -> Represents a piece. Acts as a parent class. 
        - position : Tuple(int, int)
        - value : float (maybe int)
        - side : int
        Inherited Classes:
        - The individual pieces in chess. 
            - legal_list : List[Tuple(int, int)]
            - has_moved : bool (Special attribute for rook and king)
            - a_squares : List[Type(int, int)] (Special attribute for pawn that keeps track of squares attacked by this pawn)
    - The AI Class (probably imported from another .py file)

history = List[State]

Notation: SPjmhz[SPECIAL]
    S - Side
    P - Piece Id
    j - Start File
    m - Start Rank
    h - End File
    z - End Rank
    [SPECIAL] - Special Notation: 
        - e7e8=Q (Pawn Promotion)
        - ENPAS (En Passant)
        - O-O and O-O-O (Castle)

Special Conditions/Moves:
    - Castle (Done)
        - That rook and king must have never moved.
        - No pieces in between rook and king.
        - King not in check.
        - No square between rook and king is threatened.
    - En Passant (Done)
        - Specific pawn placement.
        - Last move must be that pawn move. 
    - Stalemate (Done)
        - No possible move for player and king not in check.
    - Check (Done)
        - Player cannot make move other that moving king away, capturing source of check or blocking check.
        - Player cannot move in the direction of the check.
    - Checkmate (Done)
        - No possible move for player and king is in check. 
    - Pinned Pieces (Done)
        - If pinned to the king, it cannot move away from pin
    - Defended Pieces (Done)
        - If piece is defended, it cannot be caputure by opposite side king. 
    - Pawn Promotion (Done)
        - If pawn reached other end, promote it to another piece

AI:
    - Use MinMax(with Alpha-Beta Pruning) on board to find best move
    - Use Neural Net to prune a search tree of states. 

----------T0_DO----------:
- Create chess framework (Done)
    - Add animation like the cool kids (Done)
    - Add alpha-numeric coordinates around the board (Done) (REMOVED BECAUSE OF MOUSE IMPLEMENTATION)
    - Add board evaluation score text (Done)
    - TRY to add drag and drop (with snapping or it will suck) (ADDED CLICK AND PLACE)
    - Legal move highlighting (Done)
    - Turn Check (do last cuz it ez) (Done)
- Create legal move checking 
    - For now, do it the worst way (go through all squares and if that square is legal add it to the legal list)
        - Pawn (Done)
        - Knight (Done)
        - Bishop (Done)
        - Rook (Done)
        - Queen (Done)
        - King (Done)
- WE ARE DONE THE CHESS FRAMEWORK:
    - BUG: Pinned pieces do not take into account the blocking pieces. (FIXED)
- Implement MiniMax AI
    - For simplicity, this AI only plays black.
"""

import numpy as np
import math as m
import os
import time
from random import choice
import traceback
from graphics import *

# === Global Params ===
state_history = []
pgn = []

is_human_player = True
active_pieces = []

scale = 60
image_scale = scale/62
width = int(8*scale)
height = int(8*scale)
square_width = width//8
square_height = height//8
square_graphic_object = []
light_square_color = color_rgb(240, 217, 181)
dark_square_color = color_rgb(181, 136, 99)
highlighted_color = color_rgb(50, 50, 50)
piece_highlighted_color = color_rgb(118, 247, 150)
background_color = color_rgb(33,33,33) 
under_check_color = color_rgb(247, 118, 118)

win = GraphWin("Chess.py by Sharven", width + 100, height)
win.setBackground(background_color)

animation_speed = 1 # Higher is slower

value_text = Text(Point(width + 50, 50), 'Score')
value_text.setFace('courier')
value_text.setSize(16)
value_text.setStyle("bold")
value_text.setTextColor('white')
value_text.draw(win)

# =====================

def init(board):
    # Init Board
    for row in range(8):
        a = []
        for col in range(8):
            c = light_square_color
            if (col + row % 2) % 2 == 1:
                c = dark_square_color
            r = Rectangle(Point(row*square_height, col*square_width), Point((row+1)*square_height,(col+1)*square_width))
            r.setFill(c)
            r.setOutline(c)
            a.append(r)
            r.draw(win)
        square_graphic_object.append(a)

    # Init Pieces
    for r in board:
        for c in r:
            if type(c) != Null_Piece:
                c.graphics_object.draw(win)

def resize_images():
    from PIL import Image
    list_of_original_images = os.listdir('data/original')
    new_size = int(60 * image_scale)
    for file in list_of_original_images:
        imageFile = "data/original/"+file
        im1 = Image.open(imageFile)
        im5 = im1.resize((new_size, new_size), Image.ANTIALIAS)
        im5.save("data/scaled/"+file)

def unhighlight_all_squares():
    for row in range(8):
        for col in range(8):
            c = light_square_color
            if (col + row % 2) % 2 == 1:
                c = dark_square_color
            square_graphic_object[row][col].setFill(c)
            square_graphic_object[row][col].setOutline(c)

def notation_encoder(notation):

    srow = notation[0][0]
    scol = notation[0][1]
    erow = notation[1][0]
    ecol = notation[1][1]

    s = chr(97+scol)+str(8-srow)
    e = chr(97+ecol)+str(8-erow)    
    return (s+e)

def notation_decoder(notation):

    alpha = notation[0]
    numeric = notation[1]
    return (8-int(numeric), ord(alpha)-97)

def calculate_real_position(r, c):
    return (c*square_width + square_width//2 - 1, r*square_height + square_height//2 - 1)

def calculate_index_position(x, y):
    row = y/square_height
    col = x/square_width
    return (int(m.floor(row)), int(m.floor(col)) )

def convert_position_board_to_actual(position_board):

    board = np.empty((8,8), dtype=Piece)
    for r in range(len(position_board)):
        for c in range(len(position_board[r])):
            piece_id = abs(position_board[r][c])
            side_id = position_board[r][c]
            if piece_id != 0:
                side = (side_id/abs(side_id))
                s = 'W'
                if side == -1:
                    s = 'B'
                p = calculate_real_position(r, c)
                if piece_id == 1:
                    board[r][c] = Pawn((r,c), 1*side, side, 'P', Image(Point(p[0], p[1]), 'data/scaled/'+s+'P.png'))
                elif piece_id == 2:
                    board[r][c] = Knight((r,c), 3*side, side, 'N', Image(Point(p[0], p[1]), 'data/scaled/'+s+'N.png'))
                elif piece_id == 3:
                    board[r][c] = Bishop((r,c), 3*side, side, 'B', Image(Point(p[0], p[1]), 'data/scaled/'+s+'B.png'))
                elif piece_id == 4:
                    board[r][c] = Rook((r,c), 5*side, side, 'R', Image(Point(p[0], p[1]), 'data/scaled/'+s+'R.png'))
                elif piece_id == 5:
                    board[r][c] = Queen((r,c), 9*side, side, 'Q', Image(Point(p[0], p[1]), 'data/scaled/'+s+'Q.png'))
                elif piece_id == 6:
                    board[r][c] = King((r,c), 50*side, side, 'K', Image(Point(p[0], p[1]), 'data/scaled/'+s+'K.png'))
                active_pieces.append(board[r][c])
            else:
                board[r][c] = Null_Piece((r,c))

    return board

def get_sign(x, y):
    val = y-x
    if val == 0:
        return val
    return int(val/abs(val))

def update_legal_moves(board):

    for z in active_pieces:
        z.is_defended = False

    for z in active_pieces:
        if type(z) == Pawn:
            z.a_squares.clear()
        if type(z) != King:
            z.find_legal_moves(board)

    for z in active_pieces:
        if type(z) == King:
            z.attacking_pieces.clear()
            z.find_legal_moves(board)

def get_game_status(curr_turn):
    
    insufficient_pieces = True
    for z in active_pieces:
        if type(z) != King:
            insufficient_pieces = False
    if insufficient_pieces:
        return "INSUFFICIENT MATERIAL"

    for z in active_pieces:
        if z.side == curr_turn:
            if len(z.legal_moves) > 0:
                return "CONTINUE"
    for z in active_pieces:
        if type(z) == King and z.side == curr_turn:
            if z.under_check:
                return "CHECKMATE"
            else:
                return "STALEMATE"   

def update_turn(t):
    curr_turn = 2*(t % 2) - 1
    return curr_turn

def get_all_legal_moves_for_side(side, board):
    all_legal_moves = []
    for r in board:
        for z in r:
            if z.side == side and type(z) != Null_Piece:
                for l_move in z.legal_moves:
                    all_legal_moves.append((z.position, l_move))
    return all_legal_moves

class State():
    
    def __init__(self, board_config):
        self.board = board_config
        self.evaluate_board()
        self.last_board = None

    def move(self, start, end, shallow=False):
        if start != end:
            piece = self.board[start[0]][start[1]]

            if type(piece) != Null_Piece:
                
                result = piece.check_legal(self.board, end) 
                
                if result:

                    self.last_board = self.board.copy()
                
                    if type(self.board[end[0]][end[1]]) != Null_Piece: # Capture
                        active_pieces.remove(self.board[end[0]][end[1]])
                        if not shallow:
                            self.board[end[0]][end[1]].graphics_object.undraw() 
                    elif result == "ENPASSANT": # En Passant Capture
                        if piece.side == 1: # 
                            if not shallow:
                                self.board[end[0] + 1][end[1]].graphics_object.undraw() 
                            active_pieces.remove(self.board[end[0] + 1][end[1]])
                            self.board[end[0] + 1][end[1]] = Null_Piece((end[0] + 1, end[1])) 
                        elif piece.side == -1:
                            if not shallow: 
                                self.board[end[0] - 1][end[1]].graphics_object.undraw() 
                            active_pieces.remove(self.board[end[0] - 1][end[1]])
                            self.board[end[0] - 1][end[1]] = Null_Piece((end[0] - 1, end[1]))
                    elif type(result) != bool and result[-1] == 'C': # Castle
                        if result[0] == 'W':
                            if result[1] == 'R':
                                self.move((7,7), (7,5))
                            elif result[1] == 'L':
                                self.move((7,0), (7,3))
                        elif result[0] == 'B':
                            if result[1] == 'R':
                                self.move((0,7), (0,5))
                            elif result[1] == 'L':
                                self.move((0,0), (0,3))
                                
                    if type(self.board[start[0]][start[1]]) == Pawn:
                        self.board[start[0]][start[1]].times_moved += 1
                    elif type(self.board[start[0]][start[1]]) == King or type(self.board[start[0]][start[1]]) == Rook:
                        self.board[start[0]][start[1]].has_moved = True
                    
                    self.board[end[0]][end[1]] = piece
                    self.board[start[0]][start[1]] = Null_Piece((start[0], start[1]))
                    
                    piece.position = end
                    
                    dx = end[1]-start[1]
                    dy = end[0]-start[0]
                    
                    target_x = dx*square_width
                    target_y = dy*square_height
                    step_x = target_x/animation_speed
                    step_y = target_y/animation_speed
                    for i in range(animation_speed):
                        piece.graphics_object.move(step_x, step_y)

                    if type(piece) == Pawn:
                        r = end[0]
                        c = end[1]
                        side = piece.side
                        side = (side/abs(side))
                        s = 'W'
                        if side == -1:
                            s = 'B'
                        p = calculate_real_position(r, c)
                        i = 0
                        if side == -1:
                            i = 7
                        if end[0] == i: # Reached Last Rank
                            pid = input("ENTER A PROMOTION PIECE NAME\n").lower()
                            piece.graphics_object.undraw()
                            if pid == 'n':
                                self.board[r][c] = Knight((r,c), 3*side, side, 'N', Image(Point(p[0], p[1]), 'data/scaled/'+s+'N.png'))
                            elif pid == 'b':
                                self.board[r][c] = Bishop((r,c), 3*side, side, 'B', Image(Point(p[0], p[1]), 'data/scaled/'+s+'B.png'))
                            elif pid == 'r':
                                self.board[r][c] = Rook((r,c), 5*side, side, 'R', Image(Point(p[0], p[1]), 'data/scaled/'+s+'R.png'))
                            elif pid == 'q':
                                self.board[r][c] = Queen((r,c), 9*side, side, 'Q', Image(Point(p[0], p[1]), 'data/scaled/'+s+'Q.png'))
                            active_pieces.append(self.board[r][c])
                            self.board[r][c].graphics_object.draw(win)
                    self.evaluate_board()
                    return True
                else:
                    print("Illegal Move.")
            else:
                print("Null Square Accessed.")
            return False

    def evaluate_board(self, show_score=True): # Used to just show piece difference for players
        val = 0
        for r in self.board:
            for c in r:
                if type(c) != Null_Piece:
                    val += c.value
        if show_score:
            value_text.setText(str(val))
        self.evaluated_value = val

    def __repr__(self):
        return self.board.__repr__()

    def __str__(self):
        return str(self.evaluated_value) + '\n' + self.board.__str__()

class Piece():

    def __init__(self, position, value, side, symbol, graphics_object):
        self.position = position
        self.value = value
        self.side = side
        self.symbol = symbol
        self.graphics_object = graphics_object
        self.legal_moves = []
        self.is_defended = False

    def check_legal(self, board, position):
        raise NotImplementedError

    def find_legal_moves(self, board):
        self.legal_moves.clear()
        for r in range(len(board)):
            for c in range(len(board[r])):
                if (r,c) != self.position and self.check_legal(board, (r,c)):
                    self.legal_moves.append((r,c))

    def get_symbol(self):
        s = 'W'
        if self.side == -1:
            s = 'B'
        return s+self.symbol

    def __repr__(self):
        return self.get_symbol()

class Null_Piece():
    
    def __init__(self, position):
        self.position = position
        self.side = 0

    def __repr__(self):
        return "☐ "

class Pawn(Piece): # Done

    def __init__(self, position, value, side, symbol, graphics_object):
        Piece.__init__(self, position, value, side, symbol, graphics_object)
        self.times_moved = 0
        self.a_squares = []

    def check_legal(self, board, position):

        srow = self.position[0]
        scol = self.position[1]
        erow = position[0]
        ecol = position[1]

        if self.side == 1: # Pawn Threatened Squares
            if srow-erow == 1 and abs(scol-ecol) == 1:
                self.a_squares.append(position)
        elif self.side == -1:
            if srow-erow == -1 and abs(scol-ecol) == 1:
                self.a_squares.append(position)

        for pos in self.a_squares:
            if type(board[pos[0]][pos[1]]) != Null_Piece and board[pos[0]][pos[1]].side == self.side:
                board[pos[0]][pos[1]].is_defended = True

        if self.side == 1:
            if (erow-srow > 0) or (erow-srow < -2) or abs(ecol-scol) > 1:
                return False

            if (erow-srow < -1) and self.times_moved > 0:
                return False
        else:
            if (erow-srow < 0) or (erow-srow > 2) or abs(ecol-scol) > 1:
                return False

            if (erow-srow > 1) and self.times_moved > 0:
                return False
        
        k = None
        for z in active_pieces:
            if type(z) == King and z.side == self.side: # Pinned Check
                k = z
        krow = k.position[0]
        kcol = k.position[1]
        dr = -get_sign(srow, krow)
        dc = -get_sign(scol, kcol)
        if abs(krow-srow) == abs(kcol-scol): # Diagonal Pin Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Bishop) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and (abs(get_sign(srow, erow)) != abs(dr) or abs(get_sign(scol, ecol)) != abs(dc)):
                return False 
        elif (krow-srow) == 0 or (kcol-scol) == 0: # Line Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Rook) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and (abs(get_sign(srow, erow)) != abs(dr) or abs(get_sign(scol, ecol)) != abs(dc)):
                return False

        # En Passant
        if len(pgn) > 0:
            last_move = pgn[-1]
            if last_move[1] == 'P':
                s = notation_decoder(last_move[2:4])
                e = notation_decoder(last_move[4:6])
                if self.side == 1 and last_move[0] == 'B' and erow == 2 and srow == 3:
                    if ecol-e[1] == 0 and erow-e[0] == -1 and board[e[0]][e[1]].times_moved == 1 and abs(s[0]-e[0]) == 2:
                        return "ENPASSANT"
                elif self.side == -1 and last_move[0] == 'W' and erow == 5 and srow == 4:
                    if ecol-e[1] == 0 and erow-e[0] == 1 and board[e[0]][e[1]].times_moved == 1 and abs(s[0]-e[0]) == 2:
                        return "ENPASSANT"


        if (abs(ecol-scol) == 1 and type(board[erow][ecol]) == Null_Piece):
            return False
        elif (abs(ecol-scol) == 1 and board[erow][ecol].side == self.side):
            return False
        elif (abs(ecol-scol) == 1 and abs(erow-srow) == 1 and board[erow][ecol].side != self.side):
            return True

        drow = get_sign(srow, erow)
        curr_col = scol
        curr_row = srow
        while (curr_row, curr_col) != (erow, ecol):
            curr_row += drow
            if type(board[curr_row][curr_col]) != Null_Piece:
                return False

        return True

class Knight(Piece): # Done

    def __init__(self, position, value, side, symbol, graphics_object):
        Piece.__init__(self, position, value, side, symbol, graphics_object)

    def check_legal(self, board, position):
        srow = self.position[0]
        scol = self.position[1]
        erow = position[0]
        ecol = position[1]

        valid = ((erow == srow+2 and ecol == scol-1) or
            (erow == srow+2 and ecol == scol+1) or
            (erow == srow+1 and ecol == scol-2) or
            (erow == srow+1 and ecol == scol+2) or
            (erow == srow-2 and ecol == scol-1) or
            (erow == srow-2 and ecol == scol+1) or
            (erow == srow-1 and ecol == scol-2) or
            (erow == srow-1 and ecol == scol+2))

        k = None
        for z in active_pieces:
            if type(z) == King and z.side == self.side: # Pinned Check
                k = z
        krow = k.position[0]
        kcol = k.position[1]
        dr = -get_sign(srow, krow)
        dc = -get_sign(scol, kcol)
        if abs(krow-srow) == abs(kcol-scol): # Diagonal Pin Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Bishop) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned:
                return False 
        elif (krow-srow) == 0 or (kcol-scol) == 0: # Line Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Rook) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and (abs(get_sign(srow, erow)) != abs(dr) or abs(get_sign(scol, ecol)) != abs(dc)):
                return False
            
        if valid and type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side == self.side:
            board[erow][ecol].is_defended = True

        if type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side == self.side:
            return False

        return valid

class Bishop(Piece): # Done

    def __init__(self, position, value, side, symbol, graphics_object):
        Piece.__init__(self, position, value, side, symbol, graphics_object)

    def check_legal(self, board, position):
        srow = self.position[0]
        scol = self.position[1]
        erow = position[0]
        ecol = position[1]

        if abs((erow-srow)) != abs((ecol-scol)):
            return False
        
        if type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side == self.side:
            return False

        k = None
        for z in active_pieces:
            if type(z) == King and z.side == self.side: # Pinned Check
                k = z
        krow = k.position[0]
        kcol = k.position[1]
        dr = -get_sign(srow, krow)
        dc = -get_sign(scol, kcol)
        if abs(krow-srow) == abs(kcol-scol): # Diagonal Pin Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Bishop) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and ((get_sign(srow, erow) != dr or get_sign(scol, ecol) != dc) and (get_sign(srow, erow) != -dr or get_sign(scol, ecol) != -dc)):
                return False 
        elif (krow-srow) == 0 or (kcol-scol) == 0: # Line Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Rook) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned:
                return False

        dcol = get_sign(scol, ecol)
        drow = get_sign(srow, erow)

        curr_col = scol
        curr_row = srow

        while (curr_row, curr_col) != (erow, ecol):
            curr_col += dcol
            curr_row += drow
            if type(board[curr_row][curr_col]) != Null_Piece and board[curr_row][curr_col].side == self.side:
                board[curr_row][curr_col].is_defended = True
            if (curr_row, curr_col) == (erow, ecol):
                pass
            elif type(board[curr_row][curr_col]) != Null_Piece:
                return False
        return True

class Rook(Piece): # Done

    def __init__(self, position, value, side, symbol, graphics_object):
        Piece.__init__(self, position, value, side, symbol, graphics_object)
        self.has_moved = False

    def check_legal(self, board, position):
        srow = self.position[0]
        scol = self.position[1]
        erow = position[0]
        ecol = position[1]

        if scol != ecol and srow != erow:
            return False
        
        if type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side == self.side:
            return False
        
        k = None
        for z in active_pieces:
            if type(z) == King and z.side == self.side: # Pinned Check
                k = z
        krow = k.position[0]
        kcol = k.position[1]
        dr = -get_sign(srow, krow)
        dc = -get_sign(scol, kcol)
        if abs(krow-srow) == abs(kcol-scol): # Diagonal Pin Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Bishop) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned:
                return False 
        elif (krow-srow) == 0 or (kcol-scol) == 0: # Line Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Rook) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and (abs(get_sign(srow, erow)) != abs(dr) or abs(get_sign(scol, ecol)) != abs(dc)):
                return False

        dcol = get_sign(scol, ecol)
        drow = get_sign(srow, erow)

        curr_col = scol
        curr_row = srow

        while (curr_row, curr_col) != (erow, ecol):
            curr_col += dcol
            curr_row += drow
            if type(board[curr_row][curr_col]) != Null_Piece and board[curr_row][curr_col].side == self.side:
                board[curr_row][curr_col].is_defended = True
            if (curr_row, curr_col) == (erow, ecol):
                pass
            elif type(board[int(curr_row)][int(curr_col)]) != Null_Piece:
                return False
        return True

class Queen(Piece): # Done 

    def __init__(self, position, value, side, symbol, graphics_object):
        Piece.__init__(self, position, value, side, symbol, graphics_object)

    def check_legal(self, board, position):
        srow = self.position[0]
        scol = self.position[1]
        erow = position[0]
        ecol = position[1]

        if (scol != ecol and srow != erow) and (abs((erow-srow)) != abs((ecol-scol))):
            return False
        
        if type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side == self.side:
            return False

        k = None
        for z in active_pieces:
            if type(z) == King and z.side == self.side: # Pinned Check
                k = z
        krow = k.position[0]
        kcol = k.position[1]
        dr = -get_sign(srow, krow)
        dc = -get_sign(scol, kcol)
        if abs(krow-srow) == abs(kcol-scol): # Diagonal Pin Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Bishop) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and ((get_sign(srow, erow) != dr or get_sign(scol, ecol) != dc) and (get_sign(srow, erow) != -dr or get_sign(scol, ecol) != -dc)):
                return False
        elif (krow-srow) == 0 or (kcol-scol) == 0: # Line Check
            curr_col = scol
            curr_row = srow
            is_pinned = False
            while (curr_row < 7 and curr_row > 0) and (curr_col < 7 and curr_col > 0):
                curr_row += dr
                curr_col += dc
                if (type(board[curr_row][curr_col]) == Queen or type(board[curr_row][curr_col]) == Rook) and board[curr_row][curr_col].side != self.side:
                    is_pinned = True
                elif type(board[curr_row][curr_col]) != Null_Piece:
                    break
            if is_pinned and (abs(get_sign(srow, erow)) != abs(dr) or abs(get_sign(scol, ecol)) != abs(dc)):
                return False

        dcol = get_sign(scol, ecol)
        drow = get_sign(srow, erow)

        curr_col = scol
        curr_row = srow

        while (curr_row, curr_col) != (erow, ecol):
            curr_col += dcol
            curr_row += drow
            if type(board[curr_row][curr_col]) != Null_Piece and board[curr_row][curr_col].side == self.side:
                board[curr_row][curr_col].is_defended = True
            if (curr_row, curr_col) == (erow, ecol):
                pass
            elif type(board[int(curr_row)][int(curr_col)]) != Null_Piece:
                return False
        return True

class King(Piece): # Done

    def __init__(self, position, value, side, symbol, graphics_object):
        Piece.__init__(self, position, value, side, symbol, graphics_object)
        self.under_check = False
        self.has_moved = False
        self.t_squares = []
        self.attacking_pieces = []
        self.surrounding_squares = []

    def get_surrounding_squares(self):
        self.surrounding_squares.clear()
        row = self.position[0]
        col = self.position[1]
        self.surrounding_squares.append((row-1,col-1))
        self.surrounding_squares.append((row-1,col  ))
        self.surrounding_squares.append((row-1,col+1))
        self.surrounding_squares.append((row , col-1))
        self.surrounding_squares.append((row ,col +1))
        self.surrounding_squares.append((row+1,col-1))
        self.surrounding_squares.append((row+1,col  ))
        self.surrounding_squares.append((row+1,col+1))

        for p in self.surrounding_squares:
            if p[0] < 0 or p[0] > 7 or p[1] < 0 or p[1] > 7:
                self.surrounding_squares.remove(p)

    def get_t_squares(self, board):
        self.t_squares.clear()
        for p in active_pieces:
            if p.side != self.side:
                moves = None
                if type(p) != Pawn:
                    moves = p.legal_moves
                else:
                    moves = p.a_squares
                for m in moves:
                    if m not in self.t_squares:
                        self.t_squares.append(m)
                    if self.position == m and p not in self.attacking_pieces:
                        self.attacking_pieces.append(p)
        
    def check_legal(self, board, position):
        srow = self.position[0]
        scol = self.position[1]
        erow = position[0]
        ecol = position[1]
        
        if type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side == self.side:
            if board[erow][ecol].side == self.side and (abs(srow-erow) <= 1 and abs(scol-ecol) <= 1):
                board[erow][ecol].is_defended = True
            return False

        self.get_t_squares(board)

        if self.position in self.t_squares: # Under Check!
            self.under_check = True
        else:
            self.under_check = False

        if self.under_check: # Restrict Moves Because of Check
            valid_squares = []
            for ap in self.attacking_pieces:
                if type(ap) != Pawn and type(ap) != Knight: # Blockable Checks
                    dcol = get_sign(scol, ap.position[1])
                    drow = get_sign(srow, ap.position[0])
                    curr_col = scol
                    curr_row = srow
                    while (curr_row, curr_col) != (ap.position[0], ap.position[1]):
                        curr_col += dcol
                        curr_row += drow
                        if (curr_row, curr_col) not in valid_squares:
                            valid_squares.append((curr_row, curr_col))
                else: # Unblockable Checks
                    valid_squares.append(ap.position)
            for z in active_pieces:
                if type(z) != King and z.side == self.side:
                    for legal_move in z.legal_moves:
                        if legal_move not in valid_squares:
                            z.legal_moves.remove(legal_move)

        if self.under_check:
            for ap in self.attacking_pieces:
                if type(ap) != Pawn and type(ap) != Knight: # Line Checks
                    dcol = -get_sign(scol, ap.position[1])
                    drow = -get_sign(srow, ap.position[0])
                    if scol + dcol == ecol and srow + drow == erow:
                        return False

        if position in self.t_squares: # Threatened Square Check
            return False

        if not self.under_check and not self.has_moved: # Castling
            if self.side == 1:
                if erow == 7 and ecol == 6 and (erow, ecol - 1) not in self.t_squares:
                    if type(board[7][7]) == Rook and not board[7][7].has_moved: # WRC
                        return "WRC"
                elif erow == 7 and ecol == 2 and (erow, ecol + 1) not in self.t_squares:
                    if type(board[7][0]) == Rook and not board[7][0].has_moved: # WLC
                        return "WLC"
            elif self.side == -1:
                if erow == 0 and ecol == 6 and (erow, ecol - 1) not in self.t_squares:
                    if type(board[0][7]) == Rook and not board[0][7].has_moved: # BRC
                        return "BRC"
                elif erow == 0 and ecol == 2 and (erow, ecol + 1) not in self.t_squares:
                    if type(board[0][0]) == Rook and not board[0][0].has_moved: # BLC
                        return "BLC"

        if type(board[erow][ecol]) != Null_Piece and board[erow][ecol].side != self.side and board[erow][ecol].is_defended: # Defended Piece Check
            return False
            
        if abs(srow-erow) > 1 or abs(scol-ecol) > 1:
            return False

        k = None
        for z in active_pieces:
            if type(z) == King and z.side != self.side:
                k = z
        k.get_surrounding_squares()        
        if position in k.surrounding_squares: # Anti King Clash
            return False

        return True

class MinMax(): # THE AI
    def __init__(self, start_state):
        self.root_state = start_state

    def find_best_move(self, depth, curr_state, is_maximizing_player):

        if depth == 0:
            return -curr_state.evaluated_value

        list_of_legal_moves = None
        if (is_maximizing_player):
            list_of_legal_moves = get_all_legal_moves_for_side(-1, curr_state.board)
            best = -999999
            for move in list_of_legal_moves:
                curr_state.move(move[0], move[1], shallow=True)
                best  = max(best, self.find_best_move(depth - 1, curr_state, not is_maximizing_player))
                curr_state.board = curr_state.last_board
            return best
        else:
            list_of_legal_moves = get_all_legal_moves_for_side(1, curr_state.board)
            best = 999999
            for move in list_of_legal_moves:
                curr_state.move(move[0], move[1], shallow=True)
                best  = min(best, self.find_best_move(depth - 1, curr_state, not is_maximizing_player))
                curr_state.board = curr_state.last_board
            return best
        

def main():
    resize_images()
    start_board = np.asarray([[-4,-2,-3,-5,-6,-3,-2,-4],
                              [-1,-1,-1,-1,-1,-1,-1,-1],
                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                              [ 0, 0, 0, 0, 0, 0, 0, 0],
                              [ 1, 1, 1, 1, 1, 1, 1, 1],
                              [ 4, 2, 3, 5, 6, 3, 2, 4]])
    # start_board = np.asarray([[ 0, 0, 0, 0,-6, 0,-5, 0],
    #                           [ 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [ 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [ 0, 0, 0, 5, 0, 0, 0, 0],
    #                           [ 0, 0, 0, 0, 0, 0, 0, 0],
    #                           [ 0, 6, 0, 0, 0, 0, 0, 0],
    #                           [ 0, 0, 0, 0, 0, 0,-3, 0],
    #                           [ 0, 0, 0, 0, 0, 0, 0, 0]])
    board = convert_position_board_to_actual(start_board)
    init(board)
    current_state = State(board)
    m = MinMax(State(current_state.board.copy()))
    state_history.append(current_state.board.copy())
    turn_count = 1
    curr_turn = 0
    spos = None
    epos = None
    while True:
        
        try:
            curr_turn = update_turn(turn_count)
            update_legal_moves(current_state.board)
            status = get_game_status(curr_turn)
            if status != "CONTINUE":
                print("GAME OVER:",status)
                return

            for z in active_pieces: # Check for checks
                if type(z) == King and z.under_check:
                    pos = z.position
                    print("CHECK!")
                    square_graphic_object[pos[1]][pos[0]].setFill(under_check_color)
                    square_graphic_object[pos[1]][pos[0]].setOutline(under_check_color)

            if curr_turn == 1:
           
                mouse = win.getMouse()
                spos = calculate_index_position(mouse.getX(), mouse.getY())
                
                if type(current_state.board[spos[0]][spos[1]]) != Null_Piece and current_state.board[spos[0]][spos[1]].side == curr_turn:
                    square_graphic_object[spos[1]][spos[0]].setFill(piece_highlighted_color)
                    square_graphic_object[spos[1]][spos[0]].setOutline(piece_highlighted_color)
                    for move in current_state.board[spos[0]][spos[1]].legal_moves:
                        square_graphic_object[move[1]][move[0]].setFill(highlighted_color)
                        square_graphic_object[move[1]][move[0]].setOutline(highlighted_color)
                    mouse = win.getMouse()
                    epos = calculate_index_position(mouse.getX(), mouse.getY()) 
                
            elif curr_turn == -1:
                m.root_state = State(current_state.board.copy())
                m_move = m.find_best_move(4, m.root_state, True)
                spos = m_move[0]
                epos = m_move[1]
            
            if curr_turn == 1:
                start = spos
                end = epos
            else:
                start = m_move[0]
                end = m_move[1]

            if type(current_state.board[spos[0]][spos[1]]) != Null_Piece:
                current_state = State(current_state.board.copy())
                nota = current_state.board[spos[0]][spos[1]].get_symbol()+notation_encoder((start, end))
                if current_state.move(start, end):
                    pgn.append(nota)
                    state_history.append(current_state)
                    turn_count += 1
            unhighlight_all_squares()

        except Exception as e:
            if str(e) == "getMouse in closed window":
                quit()
            # print(f"Exception: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
    