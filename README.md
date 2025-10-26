# 🎲 Arthvidya Monopoly - Multi-Client System

A comprehensive multiplayer Monopoly game with both Pygame desktop interface and Streamlit web interface for remote players.

## 🌟 Features

### 🎮 Pygame Desktop Game
- Full-featured Monopoly game with modern UI
- Sound effects and animations
- Property trading system
- Chance and mystery cards
- Bankruptcy system
- Undo functionality

### 🌐 Streamlit Web Interface
- **Control Center**: Game master interface for managing the game
- **Team Interfaces**: Individual interfaces for each of the 5 teams
- **Real-time Updates**: Live game state synchronization
- **Interactive Controls**: Players can make moves through the web interface
- **Game Logging**: Complete game history and messaging

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Required packages (install with `pip install -r requirements.txt`)

### Installation

1. **Clone or download the game files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the multi-client system**:
   ```bash
   python start_game.py
   ```

### Access Points

- **Control Center**: http://localhost:8501
- **Team Interfaces**: http://localhost:8501 (select team from sidebar)

## 🎯 How to Use

### For Game Master (Control Center)

1. **Open Control Center**: Navigate to http://localhost:8501
2. **Monitor Game State**: View current player, team status, and game phase
3. **Control Game Flow**: 
   - Roll dice for current player
   - Advance turns
   - Manage properties
   - Execute special actions
4. **Monitor Player Actions**: See pending actions from players
5. **View Game Log**: Track all game events

### For Players (Team Interfaces)

1. **Select Your Team**: Choose your team from the sidebar
2. **Wait for Your Turn**: Interface shows when it's your turn
3. **Make Your Move**: Use the action buttons when it's your turn:
   - Roll dice
   - Buy/sell properties
   - Take chance cards
   - Spin mystery wheel
   - Start trading
4. **View Game Status**: See your balance, position, and properties
5. **Read Messages**: Stay updated with game events

## 🎮 Game Controls

### Control Center Commands
- **🎲 Roll Dice**: Roll dice for current player
- **⏭️ Next Turn**: Advance to next player
- **🏠 Buy Property**: Purchase current property
- **💰 Sell Property**: Sell owned properties
- **🎲 Test Chance**: Trigger chance card
- **🔮 Test Mystery**: Trigger mystery wheel
- **🤝 Start Trading**: Begin property trading
- **🔄 Reset Game**: Reset entire game

### Player Actions
- **🎲 Roll Dice**: Request dice roll (current player only)
- **⏭️ End Turn**: End your turn
- **🏠 Buy Property**: Request property purchase
- **💰 Sell Property**: Request property sale
- **🎲 Take Chance**: Accept chance card
- **🔮 Spin Mystery**: Spin mystery wheel
- **🤝 Start Trading**: Begin trading session

## 🔧 Technical Details

### File Structure
```
arthvidya_monopoly_v2/
├── main.py                 # Main Pygame game
├── streamlit_client.py    # Streamlit web interface
├── game_integration.py     # Integration between game and web
├── start_game.py          # Startup script
├── requirements.txt       # Python dependencies
├── game_state.json        # Game state file (auto-generated)
├── player_actions.json    # Player actions file (auto-generated)
└── control_commands.json  # Control commands file (auto-generated)
```

### Communication System
- **JSON Files**: Game state and commands are shared via JSON files
- **Real-time Updates**: Web interface refreshes automatically
- **Bidirectional**: Both game master and players can send commands

### Integration Points
The system uses file-based communication between the Pygame game and Streamlit interface:
- Game state is written to `game_state.json`
- Player actions are written to `player_actions.json`
- Control commands are written to `control_commands.json`

## 🎲 Game Rules

### Basic Gameplay
- 5 teams compete to accumulate wealth and properties
- Roll dice to move around the board
- Buy properties when landing on them
- Collect rent from other players
- Use chance cards and mystery wheel for special effects

### Special Spaces
- **Chance Spaces**: Answer questions for rewards
- **Mystery Wheel**: Spin for random effects
- **Penalty Spaces**: Pay fines or skip turns
- **Free Parking**: Safe space with no action

### Trading System
- Players can trade properties with each other
- Set custom offer amounts
- Accept or decline trades
- Money and properties transfer automatically

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   - Change port in `start_game.py` (line with `--server.port`)
   - Or kill existing processes: `pkill -f streamlit`

2. **Game Won't Start**:
   - Check Python version: `python --version`
   - Install dependencies: `pip install -r requirements.txt`
   - Check file permissions

3. **Web Interface Not Loading**:
   - Check if Streamlit is running: `ps aux | grep streamlit`
   - Try accessing: http://127.0.0.1:8501
   - Check firewall settings

4. **No Sound Effects**:
   - Check system volume
   - Verify audio drivers
   - Run as administrator if needed

### Debug Mode
- Check console output for error messages
- Monitor JSON files for state updates
- Use browser developer tools for web interface issues

## 🎯 Advanced Usage

### Customization
- Modify team colors in `streamlit_client.py`
- Adjust game rules in `main.py`
- Customize UI in Streamlit components

### Network Access
- Change `--server.address` to `0.0.0.0` for network access
- Use port forwarding for remote access
- Set up reverse proxy for production use

### Integration
- Connect to external databases
- Add user authentication
- Implement game statistics tracking

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console output for errors
3. Verify all dependencies are installed
4. Check file permissions and paths

## 🎉 Enjoy Your Game!

Have fun playing Arthvidya Monopoly with your friends! The multi-client system makes it easy to manage games remotely and provides a great experience for all players.
