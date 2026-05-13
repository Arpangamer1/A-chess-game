"""Chess piece definitions and movement rules."""

class Piece:
    """Base class for chess pieces."""
    
    def __init__(self, color, position=None):
        """
        Initialize a piece.
        
        Args:
            color: 'white' or 'black'
            position: tuple (row, col) or None
        """
        self.color = color
        self.position = position
        self.moved = False  # Track if piece has moved (for castling/pawn double moves)
    
    def __repr__(self):
        return f"{self.color[0].upper()}{self.__class__.__name__[0]}"
    
    def get_symbol(self):
        """Return unicode symbol for piece."""
        symbols = {
            'white': {'Pawn': '♙', 'Knight': '♘', 'Bishop': '♗', 'Rook': '♖', 'Queen': '♕', 'King': '♔'},
            'black': {'Pawn': '♟', 'Knight': '♞', 'Bishop': '♝', 'Rook': '♜', 'Queen': '♛', 'King': '♚'}
        }
        return symbols[self.color].get(self.__class__.__name__, '?')


class Pawn(Piece):
    """Pawn piece."""
    
    def get_possible_moves(self, board):
        """Get all possible pawn moves."""
        moves = []
        row, col = self.position
        direction = -1 if self.color == 'white' else 1
        
        # Move forward one square
        new_row = row + direction
        if 0 <= new_row < 8 and board[new_row][col] is None:
            moves.append((new_row, col))
            
            # Move forward two squares from starting position
            if not self.moved:
                new_row_2 = row + 2 * direction
                if board[new_row_2][col] is None:
                    moves.append((new_row_2, col))
        
        # Capture diagonally
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            new_row = row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target and target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves


class Knight(Piece):
    """Knight piece."""
    
    def get_possible_moves(self, board):
        """Get all possible knight moves."""
        moves = []
        row, col = self.position
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves


class Bishop(Piece):
    """Bishop piece."""
    
    def get_possible_moves(self, board):
        """Get all possible bishop moves."""
        moves = []
        row, col = self.position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                else:
                    if target.color != self.color:
                        moves.append((new_row, new_col))
                    break
                new_row += dr
                new_col += dc
        
        return moves


class Rook(Piece):
    """Rook piece."""
    
    def get_possible_moves(self, board):
        """Get all possible rook moves."""
        moves = []
        row, col = self.position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                else:
                    if target.color != self.color:
                        moves.append((new_row, new_col))
                    break
                new_row += dr
                new_col += dc
        
        return moves


class Queen(Piece):
    """Queen piece."""
    
    def get_possible_moves(self, board):
        """Get all possible queen moves (combination of rook and bishop)."""
        moves = []
        row, col = self.position
        directions = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1),
            (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                else:
                    if target.color != self.color:
                        moves.append((new_row, new_col))
                    break
                new_row += dr
                new_col += dc
        
        return moves


class King(Piece):
    """King piece."""
    
    def get_possible_moves(self, board):
        """Get all possible king moves."""
        moves = []
        row, col = self.position
        directions = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1),
            (0, 1), (1, -1), (1, 0), (1, 1)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        # TODO: Add castling logic
        
        return moves
