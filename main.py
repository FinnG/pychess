
import operator

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
    class KING(object): pass #TODO: indicates take, but of the oppo's king
    class CHECK(object): pass #TODO: indicated move, but also places oppo in check
    class CHECKMATE(object): pass

class Piece(object):
    def __init__(self, board, position, color, directions=Direction.ALL, distance=None):
        self.board = board
        self.position = position
        self.color = color
        self.directions = directions
        self.distance = distance
        self.history = []

    def get_moves(self):
        moves = []        
        for direction in self.directions:
            size = self.board.size() if not self.distance else self.distance + 1
            for n in range(1, size):
                vector = map(lambda x: x*n, direction)
                new_position = map(operator.add, vector, self.position)
                action = self.board.check_position(self, new_position)
                if action == Action.MOVE:
                    moves.append(new_position)
                elif action == Action.TAKE:
                    moves.append(new_position)
                    break
                elif action == Action.NONE:
                    break
        return moves

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

class Rook(Piece):
    def __init__(self, board, position, color):
        super(Rook, self).__init__(board, position, color,
                                   Direction.STRAIGHT, None)

    def __str__(self):
        return 'R'            

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
            if action == Action.MOVE:
                moves.append(new_position)
            elif action == Action.TAKE:
                moves.append(new_position)
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
        super(King, self).__init__(board, position, color
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

    def size(self):
        return 8

    def setup_white(self):
        for x in range(8):
            p = Pawn(self, [x, 1], Color.WHITE)
            self.squares[x][1] = p

        r = Rook(self, [0, 0], Color.WHITE)
        self.squares[0][0] = r
        r2 = Rook(self, [7, 0], Color.WHITE)
        self.squares[7][0] = r2

        n = Knight(self, [1, 0], Color.WHITE)
        self.squares[1][0] = n
        n2 = Knight(self, [6, 0], Color.WHITE)
        self.squares[6][0] = n2

        b = Bishop(self, [2, 0], Color.WHITE)
        self.squares[2][0] = b
        b2 = Bishop(self, [5, 0], Color.WHITE)
        self.squares[5][0] = b2

        q = Queen(self, [3, 0], Color.WHITE)
        self.squares[3][0] = q

        k = King(self, [4, 0], Color.WHITE)
        self.squares[4][0] = k

    def setup_black(self):
        #TODO: remove duplication here
        for x in range(8):
            p = Pawn(self, [x, 6], Color.BLACK)
            self.squares[x][6] = p

        r = Rook(self, [0, 7], Color.BLACK)
        self.squares[0][7] = r
        r2 = Rook(self, [7, 7], Color.BLACK)
        self.squares[7][7] = r2

        n = Knight(self, [1, 7], Color.BLACK)
        self.squares[1][7] = n
        n2 = Knight(self, [6, 7], Color.BLACK)
        self.squares[6][7] = n2

        b = Bishop(self, [2, 7], Color.BLACK)
        self.squares[2][7] = b
        b2 = Bishop(self, [5, 7], Color.BLACK)
        self.squares[5][7] = b2

        q = Queen(self, [3, 7], Color.BLACK)
        self.squares[3][7] = q

        k = King(self, [4, 7], Color.BLACK)
        self.squares[4][7] = k

    def check_position(self, piece, position):
        x, y = position
        if x < 0 or x >= self.size:
            return Action.NONE
        
        if y < 0 or y >= self.size:
            return Action.NONE

        other_piece = self.squares[x][y]
        if other_piece != None:
            if other_piece.color == piece.color:
                return Action.NONE
            else:
                return Action.TAKE

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
            
        
def main():
    b = Board()
    print b

    print b.squares[1][0].get_moves()

if __name__ == '__main__':
    main()
