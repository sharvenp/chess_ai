import chess
from graphics import *
import numpy as np
import traceback
import math as m

graphic_board = None
scale = 70
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

animation_speed = 100 # Higher is slower

value_text = Text(Point(width + 50, 50), 'Score')
value_text.setFace('courier')
value_text.setSize(16)
value_text.setStyle("bold")
value_text.setTextColor('white')
value_text.draw(win)

piece_value_dict = {
    'P' : 1,
    'R' : 5,
    'N' : 3,
    'B' : 3,
    'Q' : 9,
    'K' : 100,
}

def init_graphics(board, graphic_board):

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

    draw_board(board, graphic_board)

def draw_board(board, graphic_board):

    for i in range(64):
        c = board.piece_at(i)
        row = i//8
        col = i-(row*8)
        if graphic_board[row][col] != None:
            graphic_board[row][col].graphics_object.draw(win)

def undraw_all(graphic_board):
    for r in graphic_board:
        for c in r:
            if c != None:
                c.graphics_object.undraw()

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

def convert_position_board_to_actual(acc_board):

    board = np.empty((8,8), dtype=Piece)
    for i in range(64):
        r = 7-(i//8)
        c = i-((i//8)*8)
        piece_id = acc_board.piece_at(i)
        if piece_id != None:
            side_id = str(piece_id)
            s = 'W'
            if side_id.islower():
                s = 'B'
            p = calculate_real_position(r, c)
            if side_id.lower() == 'p':
                board[r][c] = Piece((r,c), Image(Point(p[0], p[1]), 'data/scaled/'+s+'P.png'), 1 - side_id.islower(), side_id)
            elif side_id.lower() == 'n':
                board[r][c] = Piece((r,c), Image(Point(p[0], p[1]), 'data/scaled/'+s+'N.png'), 1 - side_id.islower(), side_id)
            elif side_id.lower() == 'b':
                board[r][c] = Piece((r,c), Image(Point(p[0], p[1]), 'data/scaled/'+s+'B.png'), 1 - side_id.islower(), side_id)
            elif side_id.lower() == 'r':
                board[r][c] = Piece((r,c), Image(Point(p[0], p[1]), 'data/scaled/'+s+'R.png'), 1 - side_id.islower(), side_id)
            elif side_id.lower() == 'q':
                board[r][c] = Piece((r,c), Image(Point(p[0], p[1]), 'data/scaled/'+s+'Q.png'), 1 - side_id.islower(), side_id)
            elif side_id.lower() == 'k':
                board[r][c] = Piece((r,c), Image(Point(p[0], p[1]), 'data/scaled/'+s+'K.png'), 1 - side_id.islower(), side_id)
        else:
            board[r][c] = None
    return board

def conver_int_to_position(square_int):
    r = 7-(square_int//8)
    c = square_int-((square_int//8)*8)
    return (r,c)

def graphic_board_move(board, graphic_board, start, end):
 
    piece = graphic_board[start[0]][start[1]]
    if graphic_board[end[0]][end[1]] != None:
        graphic_board[end[0]][end[1]].graphics_object.undraw()
    graphic_board[end[0]][end[1]] = graphic_board[start[0]][start[1]]
    graphic_board[start[0]][start[1]] = None

    dx = end[1]-start[1]
    dy = end[0]-start[0]
    
    target_x = dx*square_width
    target_y = dy*square_height
    step_x = target_x/animation_speed
    step_y = target_y/animation_speed
    for i in range(animation_speed):
        piece.graphics_object.move(step_x, step_y)

class Piece:

    def __init__(self, position, graphics_object, side, symbol):
        self.position = position
        self.graphics_object = graphics_object
        self.side = side
        self.symbol = symbol

class MinMax():

    def evaluation_function(self, board):
        s = 0
        for i in range(64):
            a = board.piece_at(i)
            p = str(a)
            if a != None:
                val = piece_value_dict[p.upper()]
                if p.islower():
                    val *= -1
                s += val
        value_text.setText(str(s))
        return s


    def run_minmax(self, depth, board, is_maximizing_player):
        list_of_moves = board.legal_moves
        best = 9000
        final_move = None
        for move in list_of_moves:
            board.push(move)
            val = self.find_best_move(depth - 1, board, -10000, 10000, not is_maximizing_player)
            board.pop()
            if val <= best:
                best = val
                final_move = move
        return final_move

    def find_best_move(self, depth, board, alpha, beta, is_maximizing_player):
        # return choice(get_all_legal_moves_for_side(-1, curr_state.board))
        
        res = board.result()
        if res == '1-0': 
            return float('inf')
        elif res == '0-1': 
            return -float('inf')
        elif res == '1/2-1/2':
            return 0

        if depth == 0:
            return self.evaluation_function(board)

        if (is_maximizing_player):
            list_of_legal_moves = board.legal_moves
            best = -999
            for move in list_of_legal_moves:
                board.push(move)
                best = max(best, self.find_best_move(depth - 1, board, alpha, beta, not is_maximizing_player))
                board.pop()
                alpha = max(alpha, best)
                if beta <= alpha:
                    return best
            return best
        else:
            list_of_legal_moves = board.legal_moves
            best = 999
            for move in list_of_legal_moves:
                board.push(move)
                best  = min(best, self.find_best_move(depth - 1, board, alpha, beta, not is_maximizing_player))
                board.pop()
                beta = min(beta, best)
                if beta <= alpha:
                    return best
            return best

def main():
        
    board = chess.Board()
    mm = MinMax()
    resize_images()
    graphic_board = convert_position_board_to_actual(board)
    init_graphics(board, graphic_board)

    turn_count = 1
    player = 1
    ai = 0

    while True:

        curr_turn = turn_count % 2

        try:
            if board.is_game_over():
                print("GAME OVER")

            move = None

            if curr_turn == player:
           
                mouse = win.getMouse()
                spos = calculate_index_position(mouse.getX(), mouse.getY())
                
                if graphic_board[spos[0]][spos[1]] != None and graphic_board[spos[0]][spos[1]].side == curr_turn:
                    square_graphic_object[spos[1]][spos[0]].setFill(piece_highlighted_color)
                    square_graphic_object[spos[1]][spos[0]].setOutline(piece_highlighted_color)
                    mouse = win.getMouse()
                    epos = calculate_index_position(mouse.getX(), mouse.getY()) 

                    nota = notation_encoder((spos, epos))
                    move =  chess.Move.from_uci(nota)

            elif curr_turn == ai:
                print('Thinking')
                move = mm.run_minmax(5, board, True)
                print("AI MOVE:", move)
            
            if move in board.legal_moves:
                # if curr_turn == ai:
                #     s = conver_int_to_position(move.from_square)
                #     e = conver_int_to_position(move.to_square)
                #     graphic_board_move(board, graphic_board, s, e)
                # elif curr_turn == player:
                #     graphic_board_move(board, graphic_board, spos, epos)
                print(move)
                board.push(move)
                undraw_all(graphic_board)
                graphic_board = convert_position_board_to_actual(board)
                draw_board(board, graphic_board)
                turn_count += 1

            unhighlight_all_squares()

        except Exception as e:
            if str(e) == "getMouse in closed window":
                quit()
            traceback.print_exc()

if __name__ == "__main__":
    main()