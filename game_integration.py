import json
import os
import time
import threading
from datetime import datetime
import subprocess
import sys

class GameIntegration:
    def __init__(self):
        self.game_state_file = "game_state.json"
        self.player_actions_file = "player_actions.json"
        self.control_commands_file = "control_commands.json"
        self.game_process = None
        self.running = False
        
    def start_game_process(self):
        """Start the pygame game process"""
        try:
            self.game_process = subprocess.Popen([sys.executable, "main.py"])
            self.running = True
            print("Game process started")
            return True
        except Exception as e:
            print(f"Failed to start game process: {e}")
            return False
    
    def stop_game_process(self):
        """Stop the pygame game process"""
        if self.game_process:
            self.game_process.terminate()
            self.game_process.wait()
            self.running = False
            print("Game process stopped")
    
    def monitor_game_state(self):
        """Monitor and update game state from the pygame game"""
        while self.running:
            try:
                # This would need to be implemented to read from your pygame game
                # For now, we'll simulate the monitoring
                time.sleep(1)
                
                # Check for control commands
                self.process_control_commands()
                
                # Check for player actions
                self.process_player_actions()
                
            except Exception as e:
                print(f"Error monitoring game state: {e}")
                time.sleep(1)
    
    def process_control_commands(self):
        """Process commands from the control center"""
        try:
            with open(self.control_commands_file, 'r') as f:
                commands = json.load(f)
            
            for timestamp, command_data in commands.items():
                command = command_data.get('command')
                
                if command == 'roll_dice':
                    self.send_to_game('R')  # Press R key
                elif command == 'next_turn':
                    self.send_to_game('E')  # Press E key
                elif command == 'buy_property':
                    self.send_to_game('B')  # Press B key
                elif command == 'sell_property':
                    self.send_to_game('S')  # Press S key
                elif command == 'test_chance':
                    self.send_to_game('C')  # Custom key for chance
                elif command == 'test_mystery':
                    self.send_to_game('M')  # Custom key for mystery
                elif command == 'start_trading':
                    self.send_to_game('T')  # Press T key
                elif command == 'reset_game':
                    self.send_to_game('RESET')  # Custom reset command
                
                # Remove processed command
                del commands[timestamp]
                with open(self.control_commands_file, 'w') as f:
                    json.dump(commands, f)
                    
        except Exception as e:
            print(f"Error processing control commands: {e}")
    
    def process_player_actions(self):
        """Process actions from players"""
        try:
            with open(self.player_actions_file, 'r') as f:
                actions = json.load(f)
            
            for team_id, action_data in actions.items():
                action = action_data.get('action')
                
                # Only process actions for the current player
                current_player = self.get_current_player()
                if team_id == current_player:
                    if action == 'roll_dice':
                        self.send_to_game('R')
                    elif action == 'end_turn':
                        self.send_to_game('E')
                    elif action == 'buy_property':
                        self.send_to_game('B')
                    elif action == 'sell_property':
                        self.send_to_game('S')
                    elif action == 'take_chance':
                        self.send_to_game('Y')  # Yes to chance
                    elif action == 'spin_mystery':
                        self.send_to_game('SPIN')  # Custom mystery spin
                    elif action == 'start_trading':
                        self.send_to_game('T')
                
                # Remove processed action
                del actions[team_id]
                with open(self.player_actions_file, 'w') as f:
                    json.dump(actions, f)
                    
        except Exception as e:
            print(f"Error processing player actions: {e}")
    
    def send_to_game(self, key_or_command):
        """Send a key press or command to the pygame game"""
        # This would need to be implemented to actually send input to your pygame game
        # For now, we'll just log it
        print(f"Sending to game: {key_or_command}")
        
        # You could implement this using:
        # 1. Named pipes
        # 2. Socket communication
        # 3. File-based communication
        # 4. Direct function calls if integrated
    
    def get_current_player(self):
        """Get the current player ID"""
        try:
            with open(self.game_state_file, 'r') as f:
                state = json.load(f)
            current_idx = state.get('current_player', 0)
            return f"T{current_idx + 1}"
        except:
            return "T1"
    
    def update_game_state(self, state_data):
        """Update the game state file"""
        try:
            with open(self.game_state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Error updating game state: {e}")
    
    def add_game_message(self, message):
        """Add a message to the game log"""
        try:
            with open(self.game_state_file, 'r') as f:
                state = json.load(f)
            
            if 'messages' not in state:
                state['messages'] = []
            
            state['messages'].append({
                'timestamp': datetime.now().isoformat(),
                'message': message
            })
            
            # Keep only last 50 messages
            state['messages'] = state['messages'][-50:]
            
            self.update_game_state(state)
        except Exception as e:
            print(f"Error adding game message: {e}")

# Integration functions for your main.py game
def init_streamlit_integration():
    """Initialize the Streamlit integration in your main game"""
    global game_integration
    game_integration = GameIntegration()
    return game_integration

def update_streamlit_state(game_instance):
    """Update the Streamlit state with current game data"""
    if not hasattr(game_instance, 'streamlit_integration'):
        return
    
    # Extract game state from your game instance
    state = {
        "current_player": game_instance.current_idx,
        "game_phase": "playing",
        "dice_rolled": not game_instance.moving,
        "current_position": game_instance.teams[game_instance.current_idx].pos,
        "properties": {},
        "teams": [],
        "messages": [],
        "pending_actions": {},
        "game_log": []
    }
    
    # Convert teams data
    for team in game_instance.teams:
        state["teams"].append({
            "id": team.team_id,
            "name": team.name,
            "color": f"#{team.color[0]:02x}{team.color[1]:02x}{team.color[2]:02x}",
            "balance": team.balance,
            "pos": team.pos
        })
    
    # Convert properties data
    for i, prop in enumerate(game_instance.properties):
        if prop["owner"] is not None:
            state["properties"][str(i)] = {
                "owner": prop["owner"],
                "name": game_instance.property_data.get(i, {}).get('name', f'Property {i}')
            }
    
    # Update the state file
    game_integration.update_game_state(state)

def log_game_event(message):
    """Log a game event to the Streamlit interface"""
    if hasattr(game_instance, 'streamlit_integration'):
        game_integration.add_game_message(message)

# Example usage in your main.py:
"""
# Add this to your Game class __init__ method:
self.streamlit_integration = init_streamlit_integration()

# Add this to your update method or main loop:
update_streamlit_state(self)

# Add logging calls throughout your game:
log_game_event(f"Team {self.teams[self.current_idx].name} rolled a {dice_result}")
log_game_event(f"Team {self.teams[self.current_idx].name} bought {property_name}")
"""
