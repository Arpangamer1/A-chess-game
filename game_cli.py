"""Command-line interface for chess game."""

import os
import sys
from chess_board import ChessBoard
from chess_ai import ChessAI
import time


class ChessGameCLI:
    """Terminal-based chess game interface."""
    
    def __init__(self):
        """Initialize the CLI game."""
        self.board = None
        self.ai = None
        self.game_mode = None
    
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_board(self):
        """Print the current board state."""
        print("\n  a b c d e f g h")
        print("  " + "−" * 15)
        
        for row in range(8):
            print(f"{8 - row}|", end=" ")
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    print(piece.get_symbol(), end=" ")
                else:
                    # Checkerboard pattern
                    print("·" if (row + col) % 2 == 0 else " ", end=" ")
            print(f"|{8 - row}")
        
        print("  " + "−" * 15)
        print("  a b c d e f g h\n")
    
    def get_position_from_input(self, prompt):
        """Get a chess position from user input."""
        while True:
            user_input = input(prompt).strip().lower()
            if len(user_input) != 2:
                print("Invalid input. Please enter a position like 'e2'")
                continue
            
            col = ord(user_input[0]) - ord('a')
            row = 8 - int(user_input[1])
            
            if not (0 <= row < 8 and 0 <= col < 8):
                print("Position out of bounds. Please try again.")
                continue
            
            return (row, col)
    
    def display_legal_moves(self, position):
        """Display legal moves for a piece."""
        legal_moves = self.board.get_legal_moves(position)
        if not legal_moves:
            return
        
        move_str = ", ".join([f"{chr(97 + m[1])}{8 - m[0]}" for m in legal_moves])
        print(f"Legal moves: {move_str}")
    
    def play_offline(self):
        """Play against AI."""
        self.clear_screen()
        print("=" * 40)
        print("      CHESS vs COMPUTER")
        print("=" * 40)
        
        print("\nDifficulty:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Expert")
        
        while True:
            choice = input("\nSelect difficulty (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                depth = int(choice)
                break
            print("Invalid choice. Please try again.")
        
        self.board = ChessBoard()
        self.ai = ChessAI(color='black', depth=depth)
        self.game_mode = 'offline'
        
        self.clear_screen()
        print("\n" + "=" * 40)
        print("     GAME STARTED - YOU ARE WHITE")
        print("=" * 40)
        print("\nEnter moves in format: e2e4 or e2 e4")
        print("Type 'quit' to exit, 'undo' to undo last move\n")
        
        self.play_game_loop()
    
    def play_game_loop(self):
        """Main game loop."""
        while True:
            self.clear_screen()
            self.print_board()
            
            # Check game end conditions
            if self.board.is_checkmate(self.board.current_player):
                winner = 'Black' if self.board.current_player == 'white' else 'White'
                print(f"Checkmate! {winner} wins!")
                break
            
            if self.board.is_stalemate(self.board.current_player):
                print("Stalemate! The game is a draw.")
                break
            
            # Check status
            player_display = "White ♔" if self.board.current_player == 'white' else "Black ♚"
            print(f"Current player: {player_display}")
            
            if self.board.is_in_check(self.board.current_player):
                print("⚠️  King is in check!")
            
            # AI move or player move
            if self.board.current_player == 'black' and self.game_mode == 'offline':
                print("\nComputer is thinking...")
                time.sleep(1)
                move = self.ai.find_best_move(self.board)
                
                if move:
                    from_pos, to_pos = move
                    from_str = f"{chr(97 + from_pos[1])}{8 - from_pos[0]}"
                    to_str = f"{chr(97 + to_pos[1])}{8 - to_pos[0]}"
                    self.board.move_piece(from_pos, to_pos)
                    print(f"Computer moved: {from_str} → {to_str}")
                else:
                    print("Computer cannot move. White wins by stalemate!")
                    break
                
                time.sleep(1)
            else:
                # Player move
                while True:
                    user_input = input("\nEnter your move (or 'help'): ").strip().lower()
                    
                    if user_input == 'quit':
                        print("Game ended.")
                        return
                    
                    if user_input == 'undo':
                        if len(self.board.move_history) >= 2:
                            self.board = ChessBoard()
                            for move in self.board.move_history[:-2]:
                                self.board.move_piece(move['from'], move['to'])
                            print("Move undone.")
                        else:
                            print("No moves to undo.")
                        break
                    
                    if user_input == 'help':
                        print("\nCommands:")
                        print("  e2e4 or e2 e4 - Move piece from e2 to e4")
                        print("  undo - Undo last move")
                        print("  board - Show current board")
                        print("  quit - Exit game")
                        continue
                    
                    if user_input == 'board':
                        break
                    
                    # Parse move input
                    try:
                        if ' ' in user_input:
                            from_str, to_str = user_input.split()
                        else:
                            if len(user_input) < 4:
                                print("Invalid format. Use 'e2e4' or 'e2 e4'")
                                continue
                            from_str = user_input[:2]
                            to_str = user_input[2:4]
                        
                        from_col = ord(from_str[0]) - ord('a')
                        from_row = 8 - int(from_str[1])
                        to_col = ord(to_str[0]) - ord('a')
                        to_row = 8 - int(to_str[1])
                        
                        if not (0 <= from_row < 8 and 0 <= from_col < 8):
                            print("Invalid starting position.")
                            continue
                        
                        if not (0 <= to_row < 8 and 0 <= to_col < 8):
                            print("Invalid ending position.")
                            continue
                        
                        piece = self.board.get_piece(from_row, from_col)
                        if not piece:
                            print("No piece at that position.")
                            continue
                        
                        if piece.color != self.board.current_player:
                            print("That's not your piece!")
                            continue
                        
                        if self.board.move_piece((from_row, from_col), (to_row, to_col)):
                            break
                        else:
                            print("Invalid move. Please try again.")
                            self.display_legal_moves((from_row, from_col))
                    
                    except (ValueError, IndexError):
                        print("Invalid input. Use format: e2e4 or e2 e4")
    
    def show_menu(self):
        """Display main menu."""
        while True:
            self.clear_screen()
            print("=" * 40)
            print("         CHESS GAME MENU")
            print("=" * 40)
            print("\n1. Play vs Computer")
            print("2. Two Player (Local)")
            print("3. Play Online")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                self.play_offline()
            elif choice == '2':
                self.play_two_player()
            elif choice == '3':
                print("\nOnline play is available through the web interface.")
                print("Run: python server.py")
                print("Then open http://localhost:5000 in your browser.")
                input("\nPress Enter to continue...")
            elif choice == '4':
                print("Thanks for playing!")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")
                input("Press Enter to continue...")
    
    def play_two_player(self):
        """Play two player local game."""
        self.clear_screen()
        print("=" * 40)
        print("      TWO PLAYER CHESS")
        print("=" * 40)
        print("\nEnter moves in format: e2e4 or e2 e4")
        print("Type 'quit' to exit\n")
        
        self.board = ChessBoard()
        self.game_mode = 'local'
        
        self.play_game_loop()


def main():
    """Run the chess game."""
    game = ChessGameCLI()
    game.show_menu()


if __name__ == '__main__':
    main()
