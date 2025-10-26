# Integration patch for main.py
# Add these modifications to your main.py file to enable Streamlit integration

# Add this import at the top of main.py
import json
import os
from datetime import datetime

# Add this to your Game class __init__ method (after line ~165):
def __init__(self):
    # ... existing initialization code ...
    
    # Streamlit integration
    self.streamlit_enabled = True
    self.game_state_file = "game_state.json"
    self.player_actions_file = "player_actions.json"
    self.control_commands_file = "control_commands.json"
    self.init_streamlit_files()

# Add these methods to your Game class:

def init_streamlit_files(self):
    """Initialize Streamlit communication files"""
    if not os.path.exists(self.game_state_file):
        self.save_streamlit_state()
    
    if not os.path.exists(self.player_actions_file):
        with open(self.player_actions_file, 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(self.control_commands_file):
        with open(self.control_commands_file, 'w') as f:
            json.dump({}, f)

def save_streamlit_state(self):
    """Save current game state for Streamlit"""
    if not self.streamlit_enabled:
        return
    
    try:
        state = {
            "current_player": self.current_idx,
            "game_phase": "playing",
            "dice_rolled": not self.moving,
            "current_position": self.teams[self.current_idx].pos if self.teams else 0,
            "properties": {},
            "teams": [],
            "messages": [],
            "pending_actions": {},
            "game_log": []
        }
        
        # Convert teams data
        for team in self.teams:
            state["teams"].append({
                "id": team.team_id,
                "name": team.name,
                "color": f"#{team.color[0]:02x}{team.color[1]:02x}{team.color[2]:02x}",
                "balance": team.balance,
                "pos": team.pos
            })
        
        # Convert properties data
        for i, prop in enumerate(self.properties):
            if prop["owner"] is not None:
                prop_name = self.property_data.get(i, {}).get('name', f'Property {i}')
                state["properties"][str(i)] = {
                    "owner": prop["owner"],
                    "name": prop_name
                }
        
        with open(self.game_state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        print(f"Error saving Streamlit state: {e}")

def log_streamlit_event(self, message):
    """Log an event to Streamlit"""
    if not self.streamlit_enabled:
        return
    
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
        
        with open(self.game_state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        print(f"Error logging Streamlit event: {e}")

def check_streamlit_commands(self):
    """Check for commands from Streamlit control center"""
    if not self.streamlit_enabled:
        return
    
    try:
        with open(self.control_commands_file, 'r') as f:
            commands = json.load(f)
        
        for timestamp, command_data in list(commands.items()):
            command = command_data.get('command')
            
            if command == 'roll_dice' and not self.moving:
                self.roll_dice()
                self.log_streamlit_event(f"Control Center: Rolled dice")
            elif command == 'next_turn':
                self.next_turn()
                self.log_streamlit_event(f"Control Center: Advanced turn")
            elif command == 'buy_property':
                self.buy_current()
                self.log_streamlit_event(f"Control Center: Attempted property purchase")
            elif command == 'sell_property':
                self._show_sell_property()
                self.log_streamlit_event(f"Control Center: Opened sell property menu")
            elif command == 'test_chance':
                self._test_chance()
                self.log_streamlit_event(f"Control Center: Triggered chance")
            elif command == 'test_mystery':
                self._test_mystery()
                self.log_streamlit_event(f"Control Center: Triggered mystery")
            elif command == 'start_trading':
                self._start_trading()
                self.log_streamlit_event(f"Control Center: Started trading")
            elif command == 'reset_game':
                self._reset_game()
                self.log_streamlit_event(f"Control Center: Reset game")
            
            # Remove processed command
            del commands[timestamp]
            with open(self.control_commands_file, 'w') as f:
                json.dump(commands, f)
                
    except Exception as e:
        print(f"Error processing Streamlit commands: {e}")

def check_streamlit_player_actions(self):
    """Check for actions from Streamlit players"""
    if not self.streamlit_enabled:
        return
    
    try:
        with open(self.player_actions_file, 'r') as f:
            actions = json.load(f)
        
        current_team_id = self.teams[self.current_idx].team_id
        
        for team_id, action_data in list(actions.items()):
            if team_id == current_team_id:
                action = action_data.get('action')
                
                if action == 'roll_dice' and not self.moving:
                    self.roll_dice()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Rolled dice")
                elif action == 'end_turn':
                    self.next_turn()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Ended turn")
                elif action == 'buy_property':
                    self.buy_current()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Attempted property purchase")
                elif action == 'sell_property':
                    self._show_sell_property()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Opened sell property menu")
                elif action == 'take_chance' and self.show_chance_confirm:
                    self._confirm_chance_yes()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Took chance")
                elif action == 'spin_mystery' and self.show_mystery:
                    self._start_spin_wheel()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Spun mystery wheel")
                elif action == 'start_trading':
                    self._start_trading()
                    self.log_streamlit_event(f"{self.teams[self.current_idx].name}: Started trading")
            
            # Remove processed action
            del actions[team_id]
            with open(self.player_actions_file, 'w') as f:
                json.dump(actions, f)
                
    except Exception as e:
        print(f"Error processing Streamlit player actions: {e}")

# Add these calls to your main game loop (in the update method):
def update(self):
    # ... existing update code ...
    
    # Check Streamlit commands and actions
    self.check_streamlit_commands()
    self.check_streamlit_player_actions()
    
    # Save state for Streamlit
    self.save_streamlit_state()

# Add logging calls throughout your game methods:

# In roll_dice method, add:
def roll_dice(self):
    # ... existing roll_dice code ...
    
    # Add this at the end:
    self.log_streamlit_event(f"{self.teams[self.current_idx].name} rolled a {d}")

# In buy_current method, add:
def buy_current(self):
    # ... existing buy_current code ...
    
    # Add this at the end:
    if self.can_buy(self.teams[self.current_idx]):
        prop_name = self.property_data.get(self.teams[self.current_idx].pos, {}).get('name', 'Property')
        self.log_streamlit_event(f"{self.teams[self.current_idx].name} bought {prop_name}")

# In next_turn method, add:
def next_turn(self):
    # ... existing next_turn code ...
    
    # Add this at the end:
    self.log_streamlit_event(f"Turn advanced to {self.teams[self.current_idx].name}")

# Add similar logging to other key methods like:
# - _trigger_chance
# - _trigger_mystery
# - _choose_trading_buyer
# - _reset_game
