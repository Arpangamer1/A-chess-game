"""Main chess game logic and board management."""

from chess_piece import Pawn, Knight, Bishop, Rook, Queen, King
import copy
import json


class ChessBoard:
    """Manages the chess board state and game rules."""
    
    def __init__(self):
        """Initialize the chess board with standard starting positions."""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.white_king = None
        self.black_king = None
        self.move_history = []
        self.current_player = 'white'
        self.setup_board()
    
    def setup_board(self):
        """Setup the board with starting chess positions."""
        # Setup pawns
        for col in range(8):
            self.board[1][col] = Pawn('black', (1, col))
            self.board[6][col] = Pawn('white', (6, col))
        
        # Setup back rank pieces
        back_rank_pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(back_rank_pieces):
            self.board[0][col] = piece_class('black', (0, col))
            self.board[7][col] = piece_class('white', (7, col))
            
            if piece_class == King:
                if self.board[0][col].color == 'black':
                    self.black_king = self.board[0][col]
                else:
                    self.white_king = self.board[7][col]
    
    def get_piece(self, row, col):
        """Get piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """Set piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
    
    def move_piece(self, from_pos, to_pos):
        """
        Move a piece from one position to another.
        
        Args:
            from_pos: tuple (row, col)
            to_pos: tuple (row, col)
        
        Returns:
            True if move was valid and executed, False otherwise
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.get_piece(from_row, from_col)
        if piece is None or piece.color != self.current_player:
            return False
        
        # Check if move is legal
        if not self.is_legal_move(from_pos, to_pos):
            return False
        
        # Execute move
        target = self.get_piece(to_row, to_col)
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        piece.position = (to_row, to_col)
        piece.moved = True
        
        # Pawn promotion
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and to_row == 0) or (piece.color == 'black' and to_row == 7):
                self.board[to_row][to_col] = Queen(piece.color, (to_row, to_col))
        
        # Record move
        self.move_history.append({
            'from': from_pos,
            'to': to_pos,
            'captured': target is not None,
            'piece': piece.__class__.__name__
        })
        
        # Switch player
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        return True
    
    def is_legal_move(self, from_pos, to_pos):
        """Check if a move is legal."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            return False
        
        # Get possible moves for the piece
        possible_moves = piece.get_possible_moves(self.board)
        if to_pos not in possible_moves:
            return False
        
        # Check if move would leave king in check
        # Create a copy to test the move
        board_copy = copy.deepcopy(self)
        target = board_copy.get_piece(to_row, to_col)
        board_copy.set_piece(to_row, to_col, piece)
        board_copy.set_piece(from_row, from_col, None)
        piece.position = (to_row, to_col)
        
        # Update king references
        if isinstance(piece, King):
            if piece.color == 'white':
                board_copy.white_king = piece
            else:
                board_copy.black_king = piece
        
        # Check if king is in check
        king_color = self.current_player
        if board_copy.is_in_check(king_color):
            return False
        
        return True
    
    def get_legal_moves(self, position):
        """Get all legal moves for piece at position."""
        from_row, from_col = position
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            return []
        
        legal_moves = []
        possible_moves = piece.get_possible_moves(self.board)
        
        for to_pos in possible_moves:
            if self.is_legal_move(position, to_pos):
                legal_moves.append(to_pos)
        
        return legal_moves
    
    def is_in_check(self, color):
        """Check if given color's king is in check."""
        king = self.white_king if color == 'white' else self.black_king
        if king is None:
            return False
        
        enemy_color = 'black' if color == 'white' else 'white'
        
        # Check if any enemy piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == enemy_color:
                    possible_moves = piece.get_possible_moves(self.board)
                    if king.position in possible_moves:
                        return True
        
        return False
    
    def is_checkmate(self, color):
        """Check if given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        
        # Check if there are any legal moves
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    if self.get_legal_moves((row, col)):
                        return False
        
        return True
    
    def is_stalemate(self, color):
        """Check if given color is in stalemate."""
        if self.is_in_check(color):
            return False
        
        # Check if there are any legal moves
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    if self.get_legal_moves((row, col)):
                        return False
        
        return True
    
    def get_board_state(self):
        """Get current board state as a 2D array of piece info."""
        state = []
        for row in range(8):
            row_state = []
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    row_state.append({
                        'type': piece.__class__.__name__,
                        'color': piece.color,
                        'symbol': piece.get_symbol()
                    })
                else:
                    row_state.append(None)
            state.append(row_state)
        return state
    
    def to_dict(self):
        """Convert board state to dictionary for transmission."""
        state = {
            'board': [],
            'current_player': self.current_player,
            'move_history': self.move_history,
            'in_check': self.is_in_check(self.current_player),
            'is_checkmate': self.is_checkmate(self.current_player),
            'is_stalemate': self.is_stalemate(self.current_player)
        }
        
        for row in range(8):
            row_data = []
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    row_data.append({
                        'type': piece.__class__.__name__,
                        'color': piece.color
                    })
                else:
                    row_data.append(None)
            state['board'].append(row_data)
        
        return state
    
    def from_dict(self, data):
        """Load board state from dictionary."""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        
        piece_classes = {
            'Pawn': Pawn, 'Knight': Knight, 'Bishop': Bishop,
            'Rook': Rook, 'Queen': Queen, 'King': King
        }
        
        for row in range(8):
            for col in range(8):
                piece_data = data['board'][row][col]
                if piece_data:
                    piece_class = piece_classes[piece_data['type']]
                    piece = piece_class(piece_data['color'], (row, col))
                    self.board[row][col] = piece
                    
                    if isinstance(piece, King):
                        if piece.color == 'white':
                            self.white_king = piece
                        else:
                            self.black_king = piece
        
        self.current_player = data.get('current_player', 'white')
        self.move_history = data.get('move_history', [])
