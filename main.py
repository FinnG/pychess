#!/usr/bin/env python
import operator
import string

class Direction(object):
    STRAIGHT = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    DIAGONAL = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    KNIGHT = [[1, 2], [-1, 2], [1, -2], [-1, -2],
              [2, 1], [-2, 1], [2, -1], [-2, -1]]
    ALL = STRAIGHT + DIAGONAL

class Color(object):
    class WHITE(object): pass
    class BLACK(object): pass

class Action(object):
    class NONE(object): pass
    class MOVE(object): pass
    class TAKE(object): pass
    class CHECK(object): pass #TODO: indicates move, but also places oppo in check
    class CHECKMATE(object): pass #TODO: indicates move, but also checkmate

class Move(object):
    def __init__(self, piece, position, action, captured):
        self.old_position = piece.position
        self.new_position = position
        self.action = action
        self.captured = captured
        self.piece = piece

    def __str__(self):
        return "%s%s%d->%s%d" % (self.piece,
                                 string.letters[self.old_position[0]],
                                 self.old_position[1] + 1,
                                 string.letters[self.new_position[0]],
                                 self.new_position[1] + 1)
    
class Piece(object):
    def __init__(self, board, position, color, directions=Direction.ALL, distance=None):
        '''Initialise a piece.

        It is intended that subclasses of the Piece class will call this method
        with the appropriate parameters to implement most of the pieces
        behaviour.

        @param board The board on which to place this piece.
        @param position A tuple of size two which signifies the position to
                        place this piece.
        @param color Signifies the colour of the piece, either `Color.WHITE`
                     or `Color.BLACK`.
        @param direction The direction in which this piece can move. Set to all
                         directions by default.
        @param distance The distance that this piece is allowed to move.
        '''
        self.board = board
        self.position = position
        self.color = color
        self.directions = directions
        self.distance = distance
        self.history = []

    def get_moves(self):
        '''Gets all legal moves that this piece can make.
        
        This method looks at the board, the directions and distance that this
        piece is allowed to move and determines a set of legal moves that this
        piece can make.

        @returns A list of dictionaries describing the moves that can be made.
        '''
        moves = []
        for direction in self.directions:
            size = self.board.size() if not self.distance else self.distance + 1
            for n in range(1, size):
                vector = map(lambda x: x*n, direction)
                new_position = map(operator.add, vector, self.position)
                action = self.board.check_position(self, new_position)
                if action == Action.MOVE or action == Action.TAKE:
                    moves.append(Move(self, new_position, action, None))
                elif action == Action.NONE:
                    break
        return moves

    def __str__(self):
        return '?'
    
    @property
    def value(self):
        return 3

class Pawn(Piece):
    def __init__(self, board, position, color):
        super(Pawn, self).__init__(board, position, color,
                                   [[0, 1]], 1)

    def get_moves(self):
        #TODO: will have to do something funky for en passant
        #TODO: add support for pawn capturing...
        if len(self.history) == 0:
            self.distance = 2
        return super(Pawn, self).get_moves()

    def __str__(self):
        return 'p'

    @property
    def value(self):
        return 1

class Rook(Piece):
    def __init__(self, board, position, color):
        super(Rook, self).__init__(board, position, color,
                                   Direction.STRAIGHT, None)

    def __str__(self):
        return 'R' 

    @property
    def value(self):
        return 5           

class Knight(Piece):
    def __init__(self,board,  position, color):
        super(Knight, self).__init__(board, position, color,
                                     Direction.KNIGHT, 1)

    def get_moves(self):
        #Implement custom get_moves as Knight can jump other pieces!
        moves = []
        for vector in self.directions:
            new_position = map(operator.add, vector, self.position)
            action = self.board.check_position(self, new_position)
            if action == Action.MOVE or action == Action.TAKE:
                moves.append(Move(self, new_position, action, None))
                break
            elif action == Action.NONE:
                break
        return moves
        
    def __str__(self):
        return 'N'

class Bishop(Piece):
    def __init__(self, board, position, color):
        super(Bishop, self).__init__(board, position, color,
                                     Direction.DIAGONAL)

    def __str__(self):
        return 'B'

class King(Piece):
    def __init__(self, board, position, color):
        super(King, self).__init__(board, position, color,
                                   Direction.ALL, 1)

    def __str__(self):
        return 'K'

    def get_moves(self):
        #TODO: add support for Castling
        return super(King, self).get_moves()

class Queen(Piece):
    def __init__(self, board, position, color):    
        super(Queen, self).__init__(board, position, color,
                                    Direction.ALL)

    def __str__(self):
        return 'Q'

    @property
    def value(self):
        return 9

class Board(object):
    def __init__(self):
        self.squares = [[None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None]]
        self.setup_white()
        self.setup_black()
        self.move_color = Color.WHITE
        self.history = {Color.WHITE: [],
                        Color.BLACK: []}
        self.captured = {Color.WHITE: [],
                         Color.BLACK: []}

    def size(self):
        return 8

    def get_next_move_color(self):
        if self.move_color == Color.WHITE:
            return Color.BLACK
        return Color.WHITE
    
    def execute_move(self, move):
        #Check that we're allowed to move this piece
        piece = move.piece
        color = piece.color
        other_color = self.get_next_move_color()
        assert self.move_color == color, "got: %r expected: %r" % (color, self.move_color)

        #Check that the piece we're moving is where we expect it to be
        old_pos = move.old_position
        assert piece.position == old_pos
        assert self.squares[old_pos[0]][old_pos[1]] == piece

        #If this move is capturing a piece, add it to the captured list
        captured_piece = move.captured #TODO this is always set to None currently!
        if captured_piece:
            self.captured[color].append(captured_piece)

        #Actually move the piece
        new_pos = move.new_position
        self.squares[old_pos[0]][old_pos[1]] = None
        self.squares[new_pos[0]][new_pos[1]] = piece
        piece.position = new_pos

        #Update the board state, ready for the next move
        self.move_color = self.get_next_move_color()
        self.history[color].append(move)

    def unexecute_move(self):
        #get the last move
        last_color = self.get_next_move_color()
        move = self.history[last_color][-1]

        #move the piece back
        old_pos = move.new_position

        captured_piece = move.captured
        if captured_piece:
            self.captured[last_color].remove(captured_piece)

        new_pos = move.old_position
        piece = self.squares[old_pos[0]][old_pos[1]]
        self.squares[old_pos[0]][old_pos[1]] = captured_piece
        self.squares[new_pos[0]][new_pos[1]] = piece
        piece.position = new_pos

        self.move_color = self.get_next_move_color()
        self.history[last_color].remove(move)

    def setup_pieces(self, piece_row=0, pawn_row=1):
        for x in range(8):
            p = Pawn(self, [x, pawn_row], Color.WHITE)
            self.squares[x][pawn_row] = p

        r = Rook(self, [0, piece_row], Color.WHITE)
        self.squares[0][piece_row] = r
        r2 = Rook(self, [7, piece_row], Color.WHITE)
        self.squares[7][piece_row] = r2

        n = Knight(self, [1, piece_row], Color.WHITE)
        self.squares[1][piece_row] = n
        n2 = Knight(self, [6, piece_row], Color.WHITE)
        self.squares[6][piece_row] = n2

        b = Bishop(self, [2, piece_row], Color.WHITE)
        self.squares[2][piece_row] = b
        b2 = Bishop(self, [5, piece_row], Color.WHITE)
        self.squares[5][piece_row] = b2

        q = Queen(self, [3, piece_row], Color.WHITE)
        self.squares[3][piece_row] = q

        k = King(self, [4, piece_row], Color.WHITE)
        self.squares[4][piece_row] = k

    def setup_white(self):
        self.setup_pieces(0, 1)

    def setup_black(self):
        self.setup_pieces(7, 6)

    def check_position(self, piece, position):
        x, y = position
        if x < 0 or x >= self.size():
            return Action.NONE
        
        if y < 0 or y >= self.size():
            return Action.NONE

        other_piece = self.squares[x][y]
        if other_piece != None:
            if other_piece.color == piece.color:
                return Action.NONE
            elif type(other_piece) == King:
                return Action.CHECK
            else:
                return Action.MOVE

        return Action.MOVE
        
    def __str__(self):
        #Really quick and dirty board print function
        result = ''
        for y in range(7, -1, -1):
            row = ''
            for x in range(8):
                if not self.squares[x][y]:
                    row += 'x'
                else:
                    row += str(self.squares[x][y])
                row += ' '
            result += row + "\n"
        return result

    def map(self, fn):
        for y in range(7, -1, -1):
            for x in range(8):
                fn(self.squares[x][y])


    def evaluate(self, color):
        piece_values = {
            Pawn: 100,
            Knight: 320,
            Bishop: 330,
            Rook: 500,
            Queen: 900,
            King: 20000,
        }

        piece_square_values = {
            Pawn: [[0,  0,  0,  0,  0,  0,  0,  0],
                   [5, 10, 10,-20,-20, 10, 10,  5,],
                   [5, -5,-10,  0,  0,-10, -5,  5,],
                   [0,  0,  0, 20, 20,  0,  0,  0,],
                   [5,  5, 10, 25, 25, 10,  5,  5,],
                   [10, 10, 20, 30, 30, 20, 10, 10,],
                   [50, 50, 50, 50, 50, 50, 50, 50,],
                   [0,  0,  0,  0,  0,  0,  0,  0,],],
            Knight: [[-50,-40,-30,-30,-30,-30,-40,-50,],
                     [-40,-20,  0,  5,  5,  0,-20,-40,],
                     [-30,  5, 10, 15, 15, 10,  5,-30,],
                     [-30,  0, 15, 20, 20, 15,  0,-30,],
                     [-30,  5, 15, 20, 20, 15,  5,-30,],
                     [-30,  0, 10, 15, 15, 10,  0,-30,],
                     [-40,-20,  0,  0,  0,  0,-20,-40,],
                     [-50,-40,-30,-30,-30,-30,-40,-50,],],
            Bishop: [[-20,-10,-10,-10,-10,-10,-10,-20,],
                     [-10,  5,  0,  0,  0,  0,  5,-10,],
                     [-10, 10, 10, 10, 10, 10, 10,-10,],
                     [-10,  0, 10, 10, 10, 10,  0,-10,],
                     [-10,  5,  5, 10, 10,  5,  5,-10,],
                     [-10,  0,  5, 10, 10,  5,  0,-10,],
                     [-10,  0,  0,  0,  0,  0,  0,-10,],
                     [-20,-10,-10,-10,-10,-10,-10,-20,],],
            Rook: [[0,  0,  0,  5,  5,  0,  0,  0],
                   [-5,  0,  0,  0,  0,  0,  0, -5,],
                   [-5,  0,  0,  0,  0,  0,  0, -5,],
                   [-5,  0,  0,  0,  0,  0,  0, -5,],
                   [-5,  0,  0,  0,  0,  0,  0, -5,],
                   [-5,  0,  0,  0,  0,  0,  0, -5,],
                   [5, 10, 10, 10, 10, 10, 10,  5,],
                   [0,  0,  0,  0,  0,  0,  0,  0,],],
            Queen: [[-20,-10,-10, -5, -5,-10,-10,-20],
                    [-10,  0,  5,  0,  0,  0,  0,-10,],
                    [-10,  5,  5,  5,  5,  5,  0,-10,],
                    [0,  0,  5,  5,  5,  5,  0, -5,],
                    [-5,  0,  5,  5,  5,  5,  0, -5,],
                    [-10,  0,  5,  5,  5,  5,  0,-10,],
                    [-10,  0,  0,  0,  0,  0,  0,-10,],
                    [-20,-10,-10, -5, -5,-10,-10,-20,],],
            King: [[20, 30, 10,  0,  0, 10, 30, 20],
                   [20, 20,  0,  0,  0,  0, 20, 20,],
                   [-10,-20,-20,-20,-20,-20,-20,-10,],
                   [-20,-30,-30,-40,-40,-30,-30,-20,],
                   [-30,-40,-40,-50,-50,-40,-40,-30,],
                   [-30,-40,-40,-50,-50,-40,-40,-30,],
                   [-30,-40,-40,-50,-50,-40,-40,-30,],
                   [-30,-40,-40,-50,-50,-40,-40,-30,],],
            #TODO: king needs a different piece square value for endgame
        }

        pieces = self.get_pieces(color)
        score = 0
        for piece in pieces:
            piece_type = type(piece)
            pos = piece.position
            score += piece_values[piece_type] + piece_square_values[piece_type][pos[0]][pos[1]]
        return score

    def get_pieces(self, color):
        pieces = []
        for y in range(7, -1, -1):
            for x in range(8):
                piece = self.squares[x][y]
                if not piece:
                    continue

                if piece.color == color:
                    pieces.append(piece)
        return pieces

    def get_legal_moves(self):
        color = self.move_color
        pieces = self.get_pieces(color)

        moves = []
        for piece in pieces:
            moves += piece.get_moves()

        return moves

    def get_best_moves(self):
        moves = self.get_legal_moves()
        
        scores = []
        for move in moves:
            self.execute_move(move)
            print move, self.evaluate(Color.WHITE)
            scores.append(self.evaluate(Color.WHITE))
            self.unexecute_move()
        print '--'
            
        best_moves = []
        best_score = 0
        for i in range(len(scores)):
            if scores[i] > best_score:
                best_moves = [moves[i]]
                best_score = scores[i]
            elif scores[i] == best_score:
                best_moves.append(moves[i])

        return best_moves
    
def main():
    b = Board()
    print b

    moves = b.get_legal_moves()

    print '--'
    for move in moves: print move
    print '--'
    for move in b.get_best_moves(): print move
    
    # p = b.squares[1][0]
    # moves = p.get_moves()
    # print map(p.move_str, p.get_moves())
    # print b.evaluate(Color.WHITE)
    # b.execute_move(p, moves[0])
    # print b
    # print b.evaluate(Color.WHITE)
    # b.unexecute_move()
    # print b
    # print b.evaluate(Color.WHITE)

if __name__ == '__main__':
    main()
