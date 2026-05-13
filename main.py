"""Main chess game application with both CLI and web interface."""

import argparse
import sys
from game_cli import ChessGameCLI
import subprocess
import os


def run_cli():
    """Run the CLI version of the game."""
    game = ChessGameCLI()
    game.show_menu()


def run_server():
    """Run the web server."""
    print("Starting Chess Game Server...")
    print("Open your browser and navigate to http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    # Update server.py to include offline game API endpoints
    from server import app, socketio
    from chess_board import ChessBoard
    from chess_ai import ChessAI
    from flask import jsonify, request
    
    offline_games = {}
    
    @app.route('/api/move', methods=['POST'])
    def api_move():
        """Handle offline player move."""
        data = request.json
        session_id = request.remote_addr
        
        if session_id not in offline_games:
            return jsonify({'error': 'Game not found'}), 404
        
        game_data = offline_games[session_id]
        board = game_data['board']
        
        from_pos = tuple(data.get('from'))
        to_pos = tuple(data.get('to'))
        
        if board.move_piece(from_pos, to_pos):
            return jsonify({
                'success': True,
                'game_state': board.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid move'}), 400
    
    @app.route('/api/ai-move', methods=['POST'])
    def api_ai_move():
        """Get AI's move."""
        data = request.json
        session_id = request.remote_addr
        difficulty = data.get('difficulty', 3)
        
        if session_id not in offline_games:
            return jsonify({'error': 'Game not found'}), 404
        
        game_data = offline_games[session_id]
        board = game_data['board']
        ai = ChessAI(color='black', depth=difficulty)
        
        move = ai.find_best_move(board)
        if move:
            from_pos, to_pos = move
            board.move_piece(from_pos, to_pos)
        
        game_over = board.is_checkmate(board.current_player) or board.is_stalemate(board.current_player)
        
        response = {
            'game_state': board.to_dict(),
            'game_over': game_over
        }
        
        if game_over:
            if board.is_checkmate(board.current_player):
                response['reason'] = 'checkmate'
                response['winner'] = 'white' if board.current_player == 'black' else 'black'
            else:
                response['reason'] = 'stalemate'
        
        return jsonify(response)
    
    @app.route('/api/new-game', methods=['POST'])
    def api_new_game():
        """Start a new offline game."""
        session_id = request.remote_addr
        offline_games[session_id] = {
            'board': ChessBoard(),
            'ai': ChessAI(color='black', depth=3)
        }
        return jsonify({
            'game_state': offline_games[session_id]['board'].to_dict()
        })
    
    # Run the server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Chess Game - Play offline or online')
    parser.add_argument('--cli', action='store_true', help='Run command-line interface')
    parser.add_argument('--server', action='store_true', help='Run web server')
    parser.add_argument('--web', action='store_true', help='Run web server (same as --server)')
    
    args = parser.parse_args()
    
    # If no arguments, show interactive menu
    if not (args.cli or args.server or args.web):
        print("=" * 50)
        print("         CHESS GAME LAUNCHER")
        print("=" * 50)
        print("\nChoose how to play:")
        print("1. Command-line Interface (Offline/Local)")
        print("2. Web Browser (Offline/Online via Internet)")
        print("3. Exit")
        
        choice = input("\nSelect (1-3): ").strip()
        
        if choice == '1':
            run_cli()
        elif choice == '2':
            run_server()
        elif choice == '3':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice!")
            sys.exit(1)
    elif args.cli:
        run_cli()
    elif args.server or args.web:
        run_server()


if __name__ == '__main__':
    main()
