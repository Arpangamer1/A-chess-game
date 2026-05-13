"""Flask server for online multiplayer chess."""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from chess_board import ChessBoard
from chess_ai import ChessAI
import uuid
import json
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'chess-secret-key-' + str(uuid.uuid4())
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active games
games = {}  # room_id -> Game object
rooms = {}  # room_id -> room info
offline_games = {}  # session_id -> offline game data


class Game:
    """Represents an active chess game."""
    
    def __init__(self, room_id, player1_id, player1_name='Player 1'):
        """Initialize a game."""
        self.room_id = room_id
        self.board = ChessBoard()
        self.players = {
            'white': {'id': player1_id, 'name': player1_name, 'connected': True},
            'black': {'id': None, 'name': 'Waiting...', 'connected': False}
        }
        self.created_at = datetime.now()
        self.spectators = []
    
    def add_player(self, player_id, player_name='Player 2', color='black'):
        """Add a second player to the game."""
        if self.players[color]['id'] is None:
            self.players[color] = {'id': player_id, 'name': player_name, 'connected': True}
            return True
        return False
    
    def to_dict(self):
        """Convert game state to dictionary."""
        return {
            'room_id': self.room_id,
            'board': self.board.to_dict(),
            'players': self.players,
            'created_at': self.created_at.isoformat()
        }


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


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


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get list of available rooms."""
    available_rooms = []
    for room_id, room_info in rooms.items():
        game = games.get(room_id)
        if game and not game.players['black']['id']:
            available_rooms.append({
                'room_id': room_id,
                'created_by': room_info['created_by'],
                'player_count': len([p for p in game.players.values() if p['id']]),
                'created_at': room_info['created_at']
            })
    return jsonify(available_rooms)


@app.route('/api/rooms/<room_id>', methods=['GET'])
def get_room(room_id):
    """Get game state for a room."""
    if room_id not in games:
        return jsonify({'error': 'Room not found'}), 404
    
    game = games[room_id]
    return jsonify(game.to_dict())


@socketio.on('connect')
def handle_connect():
    """Handle player connection."""
    print(f"Client connected: {request.sid}")
    emit('connection_response', {'data': 'Connected to server'})


@socketio.on('create_room')
def handle_create_room(data):
    """Create a new game room."""
    room_id = str(uuid.uuid4())[:8]
    player_id = request.sid
    player_name = data.get('player_name', 'Player 1')
    
    game = Game(room_id, player_id, player_name)
    games[room_id] = game
    rooms[room_id] = {
        'created_by': player_name,
        'created_at': datetime.now().isoformat()
    }
    
    join_room(room_id)
    session[f'game_{room_id}'] = {'color': 'white', 'player_id': player_id}
    
    emit('room_created', {
        'room_id': room_id,
        'color': 'white',
        'game_state': game.to_dict()
    })
    
    print(f"Room created: {room_id}")


@socketio.on('join_room')
def handle_join_room(data):
    """Join an existing game room."""
    room_id = data.get('room_id')
    player_id = request.sid
    player_name = data.get('player_name', 'Player 2')
    
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    game = games[room_id]
    
    # Try to add as second player
    if not game.add_player(player_id, player_name, 'black'):
        # Room is full, add as spectator
        game.spectators.append({'id': player_id, 'name': player_name})
        color = 'spectator'
    else:
        color = 'black'
    
    join_room(room_id)
    session[f'game_{room_id}'] = {'color': color, 'player_id': player_id}
    
    emit('room_joined', {
        'room_id': room_id,
        'color': color,
        'game_state': game.to_dict()
    })
    
    # Notify others
    socketio.emit('player_joined', {
        'player_name': player_name,
        'color': color,
        'game_state': game.to_dict()
    }, room=room_id)
    
    print(f"Player {player_name} joined room {room_id}")


@socketio.on('make_move')
def handle_move(data):
    """Handle a player's move."""
    room_id = data.get('room_id')
    from_pos = tuple(data.get('from_pos'))
    to_pos = tuple(data.get('to_pos'))
    
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    game = games[room_id]
    
    # Validate move
    if game.board.move_piece(from_pos, to_pos):
        game_state = game.to_dict()
        
        # Broadcast to all players
        socketio.emit('move_made', {
            'from_pos': from_pos,
            'to_pos': to_pos,
            'game_state': game_state
        }, room=room_id)
        
        # Check for game end
        if game.board.is_checkmate(game.board.current_player):
            winner = 'white' if game.board.current_player == 'black' else 'black'
            socketio.emit('game_over', {
                'reason': 'checkmate',
                'winner': winner,
                'game_state': game_state
            }, room=room_id)
        elif game.board.is_stalemate(game.board.current_player):
            socketio.emit('game_over', {
                'reason': 'stalemate',
                'game_state': game_state
            }, room=room_id)
    else:
        emit('error', {'message': 'Invalid move'})


@socketio.on('get_legal_moves')
def handle_get_legal_moves(data):
    """Get legal moves for a piece."""
    room_id = data.get('room_id')
    position = tuple(data.get('position'))
    
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    game = games[room_id]
    legal_moves = game.board.get_legal_moves(position)
    
    emit('legal_moves', {
        'position': position,
        'moves': [list(move) for move in legal_moves]
    })


@socketio.on('resign')
def handle_resign(data):
    """Handle player resignation."""
    room_id = data.get('room_id')
    
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    game = games[room_id]
    winner = 'black' if game.board.current_player == 'white' else 'white'
    
    socketio.emit('game_over', {
        'reason': 'resignation',
        'winner': winner,
        'game_state': game.to_dict()
    }, room=room_id)


@socketio.on('request_draw')
def handle_draw_request(data):
    """Handle draw request."""
    room_id = data.get('room_id')
    
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    socketio.emit('draw_requested', {
        'room_id': room_id
    }, room=room_id)


@socketio.on('accept_draw')
def handle_accept_draw(data):
    """Handle draw acceptance."""
    room_id = data.get('room_id')
    
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    game = games[room_id]
    socketio.emit('game_over', {
        'reason': 'draw',
        'game_state': game.to_dict()
    }, room=room_id)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle player disconnection."""
    print(f"Client disconnected: {request.sid}")


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
