# A Chess Game - Play Online & Offline

A fully-featured chess game developed in Python with both offline AI play and online multiplayer capabilities. Play against a computer opponent with adjustable difficulty levels, or challenge your friends over the internet using a room-based system.

## Features

### 🎮 Offline Mode
- Play against an AI opponent with adjustable difficulty levels (Easy, Medium, Hard, Expert)
- Full chess rules implementation including check, checkmate, and stalemate detection
- AI uses minimax algorithm with alpha-beta pruning for intelligent moves
- Piece position evaluation for better strategic play

### 👥 Online Mode
- Play with friends anywhere in the world via the internet
- Room-based system: Create a private game room and share the room ID with your friend
- Real-time move synchronization between players
- Draw requests and resignation options

### 💻 Interfaces
- **Command-Line Interface (CLI)** - Complete terminal-based game with full chess rules
- **Web Interface** - Beautiful web-based board with drag-and-drop support (in development)

## Installation

### Requirements
- Python 3.7+
- pip (Python package manager)

### Setup

1. Clone or navigate to the repository:
```bash
cd /workspaces/A-chess-game
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the main launcher:
```bash
python main.py
```

This will show an interactive menu with options to:
1. Play via Command-Line Interface
2. Play via Web Browser
3. Exit

### CLI Game (Terminal)

Start the CLI directly:
```bash
python main.py --cli
```

Or simply run:
```bash
python game_cli.py
```

#### CLI Game Commands:
- **Move a piece**: Enter positions like `e2e4` or `e2 e4` (algebraic notation)
- **Undo**: Type `undo` to undo your last move
- **Show board**: Type `board` to redisplay the current board
- **Quit**: Type `quit` to exit the game

#### Example Moves:
- `e2e4` - Move piece from e2 to e4
- `b1c3` - Develop knight
- `e7e5` - Opponent's move
- Type `help` for more commands

### Web Interface (Browser)

Start the web server:
```bash
python server.py
```

Or use the main launcher:
```bash
python main.py --server
```

Then open your browser and navigate to:
```
http://localhost:5000
```

#### Web Features:
- **Play vs Computer** - Select difficulty level and play against AI
- **Play Online** - Create or join game rooms with friends
- **Beautiful Board Interface** - Interactive chess board with piece highlighting
- **Game Status Panel** - Shows current player, check status, and move history

### Online Multiplayer

1. **Create a Room**:
   - Open http://localhost:5000
   - Click "Play Online"
   - Click "Create New Room"
   - Enter your name and click "Create Room"
   - Share the Room ID with your friend

2. **Join a Room**:
   - Open http://localhost:5000
   - Click "Play Online"
   - Click "Join Existing Room"
   - Click "Join" on the room created by your friend

3. **Play**:
   - Click on a piece to see legal moves (highlighted in gold)
   - Click on a highlighted square to move
   - Game alternates between white and black
   - Watch for check notifications

## Project Structure

```
A-chess-game/
├── chess_piece.py          # Piece definitions and movement rules
├── chess_board.py          # Board management and game logic
├── chess_ai.py             # AI opponent with minimax algorithm
├── game_cli.py             # Command-line interface
├── server.py               # Flask web server with Socket.io
├── main.py                 # Application launcher
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Web interface
└── README.md              # This file
```

## Game Rules

The chess game implements standard chess rules:

- ♔/♚ **Kings** move one square in any direction
- ♕/♛ **Queens** move any number of squares horizontally, vertically, or diagonally
- ♖/♜ **Rooks** move any number of squares horizontally or vertically
- ♗/♝ **Bishops** move any number of squares diagonally
- ♘/♞ **Knights** move in an L-shape (2+1 squares)
- ♙/♟ **Pawns** move forward one square (or two from starting position), capture diagonally

Special rules:
- **Check**: King is under attack
- **Checkmate**: King is in check with no legal moves (opponent wins)
- **Stalemate**: Player has no legal moves but king is not in check (draw)
- **Pawn Promotion**: Pawn reaching the opposite end becomes a Queen

## AI Difficulty Levels

The AI opponent uses minimax algorithm with different search depths:

- **Easy (Depth 1)**: Makes quick moves, less strategic
- **Medium (Depth 2)**: Balances speed and strategy
- **Hard (Depth 3)**: Challenging opponent, strategic play
- **Expert (Depth 4)**: Very strong opponent, slow but excellent moves

## Architecture

### Core Components

1. **chess_piece.py** - Piece classes with movement validation
   - Pawn, Knight, Bishop, Rook, Queen, King
   - Each piece implements `get_possible_moves()` method

2. **chess_board.py** - Board state and game rules
   - 8x8 board representation
   - Legal move validation (doesn't leave king in check)
   - Check/checkmate/stalemate detection

3. **chess_ai.py** - Intelligent opponent
   - Minimax algorithm with alpha-beta pruning
   - Piece evaluation and position scoring
   - Adjustable search depth for difficulty levels

4. **game_cli.py** - Terminal-based interface
   - Board display with Unicode chess symbols
   - User input processing
   - Local two-player support

5. **server.py** - Flask/Socket.io web server
   - Multiplayer game management
   - Room-based architecture
   - Real-time move updates
   - API endpoints for offline play

## Network Architecture

For online play, the system uses:
- **Flask** - Web server for serving the interface
- **Socket.io** - Real-time bidirectional communication between players
- **Rooms** - Each game is isolated in a Socket.io room

Players connect to the server, and moves are broadcast to all players in the room in real-time.

## Recent Updates

- ✅ Complete chess piece implementation with all movement rules
- ✅ Intelligent AI opponent with minimax algorithm
- ✅ Full game logic (check, checkmate, stalemate)
- ✅ Command-line interface with full game support
- ✅ Web server with room-based multiplayer
- ✅ Beautiful web interface with board display
- ✅ Offline AI play support
- ✅ Online multiplayer infrastructure

## Known Limitations

- Castling not yet implemented
- En passant not yet implemented
- Promotion automatically converts to Queen (no choice)
- Web interface board interaction in progress

## Future Enhancements

- [ ] Castling support
- [ ] En passant capture
- [ ] Promotion piece selection
- [ ] Game replay feature
- [ ] Elo rating system
- [ ] Tournament mode
- [ ] User accounts and statistics
- [ ] Mobile app version
- [ ] Voice/video chat in online games

## Development

To contribute or modify the game:

1. Chess logic changes: Edit `chess_piece.py` and `chess_board.py`
2. AI improvements: Modify `chess_ai.py` (evaluation function or search algorithm)
3. CLI interface: Update `game_cli.py`
4. Web interface: Modify `templates/index.html` and `server.py`

## Testing

Test the chess logic:
```python
from chess_board import ChessBoard

board = ChessBoard()
# Test a move
board.move_piece((6, 4), (4, 4))  # e2 to e4
print(board.current_player)  # Should be 'black'
```

Test the AI:
```python
from chess_board import ChessBoard
from chess_ai import ChessAI

board = ChessBoard()
ai = ChessAI(color='black', depth=3)
best_move = ai.find_best_move(board)
print(best_move)  # Returns ((from_row, from_col), (to_row, to_col))
```

## License

Free to use and modify for personal or educational purposes.

## Credits

Developed as a complete chess implementation with both AI and online multiplayer capabilities.

---

**Enjoy your games!** 🏆♟️
