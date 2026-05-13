"""AI bot for chess game using minimax algorithm."""

import copy
from chess_board import ChessBoard
from chess_piece import Pawn, Knight, Bishop, Rook, Queen, King


class ChessAI:
    """AI player for chess using minimax with alpha-beta pruning."""
    
    # Piece values for evaluation
    PIECE_VALUES = {
        'Pawn': 1,
        'Knight': 3,
        'Bishop': 3,
        'Rook': 5,
        'Queen': 9,
        'King': 0  # King is priceless
    }
    
    # Position scores (better positions for pieces)
    POSITION_WEIGHTS = {
        'Pawn': [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        'Knight': [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ],
        'Bishop': [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ],
        'Rook': [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ],
        'Queen': [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ],
        'King': [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]
    }
    
    def __init__(self, color='black', depth=3):
        """Initialize AI."""
        self.color = color
        self.enemy_color = 'white' if color == 'black' else 'black'
        self.depth = depth
    
    def find_best_move(self, board):
        """Find the best move using minimax algorithm."""
        best_score = float('-inf')
        best_move = None
        
        # Get all possible moves
        possible_moves = self._get_all_moves(board, self.color)
        
        if not possible_moves:
            return None
        
        for from_pos, to_pos in possible_moves:
            board_copy = copy.deepcopy(board)
            board_copy.move_piece(from_pos, to_pos)
            
            score = self._minimax(board_copy, self.depth - 1, float('-inf'), float('inf'), False)
            
            if score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)
        
        return best_move
    
    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self._evaluate(board)
        
        if board.is_checkmate(self.enemy_color if is_maximizing else self.color):
            return float('inf') if is_maximizing else float('-inf')
        
        if board.is_stalemate(self.enemy_color if is_maximizing else self.color):
            return 0
        
        if is_maximizing:
            max_eval = float('-inf')
            moves = self._get_all_moves(board, self.color)
            
            for from_pos, to_pos in moves:
                board_copy = copy.deepcopy(board)
                board_copy.move_piece(from_pos, to_pos)
                
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            moves = self._get_all_moves(board, self.enemy_color)
            
            for from_pos, to_pos in moves:
                board_copy = copy.deepcopy(board)
                board_copy.move_piece(from_pos, to_pos)
                
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _evaluate(self, board):
        """Evaluate board position. Higher score is better for AI."""
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_value = self.PIECE_VALUES.get(piece.__class__.__name__, 0)
                    position_bonus = self._get_position_bonus(piece, row, col)
                    
                    piece_score = piece_value + position_bonus
                    
                    if piece.color == self.color:
                        score += piece_score
                    else:
                        score -= piece_score
        
        # Bonus for checking opponent king
        if board.is_in_check(self.enemy_color):
            score += 50
        
        return score
    
    def _get_position_bonus(self, piece, row, col):
        """Get position bonus for a piece."""
        piece_type = piece.__class__.__name__
        if piece_type not in self.POSITION_WEIGHTS:
            return 0
        
        weights = self.POSITION_WEIGHTS[piece_type]
        
        if piece.color == 'white':
            row = 7 - row  # Flip for white's perspective
        
        return weights[row][col]
    
    def _get_all_moves(self, board, color):
        """Get all legal moves for a color."""
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == color:
                    legal_moves = board.get_legal_moves((row, col))
                    for move in legal_moves:
                        moves.append(((row, col), move))
        
        return moves
