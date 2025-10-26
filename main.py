import sys
import math
import random
import time
import json
import os
from datetime import datetime
from dataclasses import dataclass
import pygame


FPS = 60
BOARD_SPACES = 24
SIDEBAR_W = 420
UI_H = 120
MARGIN = 20

CHANCE_TILES = [4, 8, 16, 20]
MYSTERY_TILES = [2, 10, 14, 22]


@dataclass
class Team:
    team_id: str
    name: str
    color: tuple
    balance: int
    pos: int


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)  # Initialize sound mixer
        pygame.display.set_caption("Arthvidya Monopoly — Python")
        # Start in windowed, resizable mode
        self.screen = pygame.display.set_mode((1400, 900), pygame.RESIZABLE)
        self.screen_w, self.screen_h = self.screen.get_size()
        self.clock = pygame.time.Clock()
        # Enhanced fonts with better typography and fallbacks
        # Try premium fonts first, then fall back to system fonts
        self.font = (pygame.font.SysFont("arial", 18, bold=True) or 
                     pygame.font.SysFont("helvetica", 18, bold=True) or 
                     pygame.font.SysFont("segoeui", 18, bold=True) or 
                     pygame.font.SysFont("bahnschrift", 18, bold=True))
        
        self.big_font = (pygame.font.SysFont("arial", 28, bold=True) or 
                         pygame.font.SysFont("helvetica", 28, bold=True) or 
                         pygame.font.SysFont("segoeui", 28, bold=True) or 
                         pygame.font.SysFont("bahnschrift", 28, bold=True))
        
        # Premium heading fonts
        self.title_font = (pygame.font.SysFont("arial black", 42, bold=True) or 
                           pygame.font.SysFont("impact", 42, bold=True) or 
                           pygame.font.SysFont("arial", 42, bold=True) or 
                           pygame.font.SysFont("segoeui", 42, bold=True))
        
        self.subtitle_font = (pygame.font.SysFont("arial", 28, bold=True) or 
                              pygame.font.SysFont("helvetica", 28, bold=True) or 
                              pygame.font.SysFont("segoeui", 28, bold=True) or 
                              pygame.font.SysFont("bahnschrift", 28, bold=True))
        
        # Special money tracker font
        self.money_font = (pygame.font.SysFont("arial", 22, bold=True) or 
                           pygame.font.SysFont("helvetica", 22, bold=True) or 
                           pygame.font.SysFont("segoeui", 22, bold=True) or 
                           pygame.font.SysFont("bahnschrift", 22, bold=True))

        self.teams = [
            Team("T1", "Team 1", (211, 47, 47), 10_000_000, 0),
            Team("T2", "Team 2", (25, 118, 210), 10_000_000, 0),
            Team("T3", "Team 3", (56, 142, 60), 10_000_000, 0),
            Team("T4", "Team 4", (245, 124, 0), 10_000_000, 0),
            Team("T5", "Team 5", (123, 31, 162), 10_000_000, 0),
        ]
        self.current_idx = 0

        self.positions = []
        self.board_rect, self.sidebar_rect = self._compute_layout_rects()
        self.properties = [
            {"index": i, "owner": None} for i in range(BOARD_SPACES)
        ]
        self.moving = False
        self.move_steps = 0
        self.move_progress = 0.0  # 0..1 between tiles
        self.from_pos_idx = None
        self.to_pos_idx = None
        self.token_trail = {t.team_id: [] for t in self.teams}
        self.skip_next_turn = {t.team_id: False for t in self.teams}

        # Overlays
        self.show_chance = False
        self.chance_card = None
        self.chance_feedback = None
        self.feedback_timer = 0
        self.show_chance_confirm = False  # New: confirmation popup

        self.show_mystery = False
        self.mystery_card = None
        self.mystery_feedback = None
        
        # Spin wheel animation variables
        self.spinning = False
        self.spin_angle = 0
        self.spin_speed = 0
        self.spin_target_angle = 0
        self.spin_duration = 0
        self.spin_progress = 0
        self.selected_mystery = None
        
        # Randomization tracking
        self.used_mysteries = []
        self.used_chance_questions = []
        self.recent_mystery_results = []  # Track last few results to avoid repetition
        self.max_recent_results = 3  # Don't repeat within last 3 spins

        # Property selling overlay
        self.show_sell_property = False
        self.sell_property_feedback = None
        # Property trading system
        self.show_trading = False
        self.trading_seller = None
        self.trading_property = None
        self.trading_offers = {}  # {team_id: offer_amount}
        self.trading_feedback = None
        self.trading_phase = None  # 'select_property', 'collect_offers', 'choose_buyer'
        self.trading_mode = False
        self.trading_offer_amounts = {}  # {team_id: current_offer_amount}

        self.chance_cards = self._build_chance_cards()
        self.mystery_cards = self._build_mystery_cards()
        self.property_data = self._build_property_data()

        # Try loading a board image from common filenames
        self.board_image_original = None
        self.board_image_scaled = None
        for name in [
            "monopoly board.jpg",
            "monopoly_board.jpg",
            "board.jpg",
            "board.png",
        ]:
            try:
                self.board_image_original = pygame.image.load(name).convert()
                break
            except Exception:
                continue
        
        # Try to read properties from board image if available
        if self.board_image_original is not None:
            self._try_read_properties_from_image()

        self._compute_positions()

        # clickable areas collected each frame (UI buttons, money controls, chance/mystery options)
        self.click_areas = []

        self.overlay_timer = 0

        # Undo system
        self.game_history = []
        self.max_history_size = 50  # Limit history to prevent memory issues
        
        # Dice randomization tracking
        self.last_dice_roll = None
        
        # Sound system initialization
        self.sounds = self._init_sounds()
        
        # Streamlit integration
        self.streamlit_enabled = True
        self.game_state_file = "game_state.json"
        self.player_actions_file = "player_actions.json"
        self.control_commands_file = "control_commands.json"
        self.init_streamlit_files()

    def _init_sounds(self):
        """Initialize sound effects using pygame's built-in sound generation"""
        sounds = {}
        
        print("Initializing sound system...")
        print(f"Pygame mixer initialized: {pygame.mixer.get_init()}")
        
        try:
            # Generate simple sound effects using pygame's built-in sound generation
            # Dice roll sound (short beep)
            print("Creating dice sound...")
            dice_sound = self._create_beep_sound(440, 0.1)
            sounds['dice'] = dice_sound
            
            # Movement sound (step sound)
            print("Creating movement sound...")
            move_sound = self._create_beep_sound(220, 0.05)
            sounds['move'] = move_sound
            
            # Wheel spin sound (whoosh)
            print("Creating spin sound...")
            spin_sound = self._create_sweep_sound(200, 800, 0.5)
            sounds['spin'] = spin_sound
            
            # Property purchase sound (money ching)
            print("Creating purchase sound...")
            purchase_sound = self._create_chord_sound([523, 659, 784], 0.3)
            sounds['purchase'] = purchase_sound
            
            # Button click sound
            print("Creating click sound...")
            click_sound = self._create_beep_sound(800, 0.05)
            sounds['click'] = click_sound
            
            print("All sounds created successfully!")
            
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            import traceback
            traceback.print_exc()
            # Create silent sounds as fallback
            sounds = {key: None for key in ['dice', 'move', 'spin', 'purchase', 'click']}
        
        return sounds
    
    def _create_beep_sound(self, frequency, duration):
        """Create a simple beep sound without numpy"""
        try:
            import array
            import math
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            # Create stereo sound array
            sound_array = array.array('h')
            for i in range(frames):
                # Create a simple sine wave with envelope
                envelope = 0.3 * (i / frames) * (1 - i / frames)  # Fade in/out
                wave = int(16383 * envelope * math.sin(2 * math.pi * frequency * i / sample_rate))
                sound_array.append(wave)  # Left channel
                sound_array.append(wave)  # Right channel
            
            return pygame.sndarray.make_sound(sound_array)
        except Exception as e:
            print(f"Failed to create beep sound: {e}")
            return None
    
    def _create_sweep_sound(self, start_freq, end_freq, duration):
        """Create a frequency sweep sound without numpy"""
        try:
            import array
            import math
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            sound_array = array.array('h')
            for i in range(frames):
                freq = start_freq + (end_freq - start_freq) * i / frames
                envelope = 0.2 * (i / frames) * (1 - i / frames)  # Fade in/out
                wave = int(16383 * envelope * math.sin(2 * math.pi * freq * i / sample_rate))
                sound_array.append(wave)  # Left channel
                sound_array.append(wave)  # Right channel
            
            return pygame.sndarray.make_sound(sound_array)
        except Exception as e:
            print(f"Failed to create sweep sound: {e}")
            return None
    
    def _create_chord_sound(self, frequencies, duration):
        """Create a chord sound without numpy"""
        try:
            import array
            import math
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            sound_array = array.array('h')
            for i in range(frames):
                wave = 0
                envelope = 0.2 * (i / frames) * (1 - i / frames)  # Fade in/out
                for freq in frequencies:
                    wave += int(8191 * envelope * math.sin(2 * math.pi * freq * i / sample_rate))
                sound_array.append(wave)  # Left channel
                sound_array.append(wave)  # Right channel
            
            return pygame.sndarray.make_sound(sound_array)
        except Exception as e:
            print(f"Failed to create chord sound: {e}")
            return None
    
    def _play_sound(self, sound_name):
        """Play a sound effect"""
        print(f"Attempting to play sound: {sound_name}")
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                print(f"Playing {sound_name} sound...")
                self.sounds[sound_name].play()
                print(f"Sound {sound_name} played successfully")
            except Exception as e:
                print(f"Failed to play sound {sound_name}: {e}")
        else:
            print(f"Sound {sound_name} not available or is None")

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

    def _build_chance_cards(self):
        return [
            {
                "q": "A man walks 10 km north from point A, turns right, and walks 5 km. He then turns right again and walks 10 km. What is the man's final position with respect to his starting point A?",
                "options": [
                    "5 km South", 
                    "15 km East", 
                    "5 km East",
                    "10 km North"
                ],
                "answer": 2,
            },
            {
                "q": "In a family, B is the brother of A. C is the father of B. E is the mother of D. A and D are married. How is E related to C?",
                "options": ["Daughter", "Daughter-in-law", "Wife", "Mother-in-law"],
                "answer": 3,
            },
            {
                "q": "\"Ideas for life\" is the tagline of which electronics company?",
                "options": ["Samsung", "Sony", "Philips", "Panasonic"],
                "answer": 3,
            },
            {
                "q": "In the sport of polo, what is the term for a period of play?",
                "options": ["Innings", "Chukkar", "Quarter", "Round"],
                "answer": 1,
            },
            {
                "q": "The \"Golden Ball\" award is presented to the best player in which major international football tournament?",
                "options": ["UEFA European Championship", "FIFA World Cup", "Copa América", "African Cup of Nations"],
                "answer": 1,
            },
            {
                "q": "Which of the following countries is known as the \"Land of Thousand Lakes\"?",
                "options": ["Norway", "Switzerland", "Finland", "Canada"],
                "answer": 2,
            },
            {
                "q": "The Great Victoria Desert is located on which continent?",
                "options": ["Africa", "North America", "Australia", "South America"],
                "answer": 2,
            },
            {
                "q": "Which of the following bodies of water is the saltiest in the world, with a salinity of around 34%?",
                "options": ["Black Sea", "Dead Sea", "Caspian Sea", "Red Sea"],
                "answer": 1,
            },
            {
                "q": "Which bowler holds the record for the most wickets taken in Test cricket?",
                "options": ["Anil Kumble", "Shane Warne", "Muttiah Muralitharan", "James Anderson"],
                "answer": 2,
            },
            {
                "q": "The term \"Hand of God\" is most famously associated with which footballer?",
                "options": ["Pelé", "Lionel Messi", "Diego Maradona", "Cristiano Ronaldo"],
                "answer": 2,
            },
            {
                "q": "Friends are priceless… and which brand made it official with the tagline \"Har Ek Friend Zaroori Hota Hai\"?",
                "options": ["Vodafone", "Airtel", "Jio", "Idea"],
                "answer": 0,
            },
            {
                "q": "Rohit is facing north. He turns 90° right, then 45° left, and again 135° right. Which direction is he facing now?",
                "options": ["South", "South-East", "West", "North-West"],
                "answer": 2,
            },
            {
                "q": "\"Impossible is Nothing\" belongs to:",
                "options": ["Puma", "Nike", "Adidas", "Reebok"],
                "answer": 2,
            },
            {
                "q": "Which of the following sports uses a \"puck\"?",
                "options": ["Ice Hockey", "Baseball", "Polo", "Rugby"],
                "answer": 0,
            },
            {
                "q": "Which city is known as the \"City of Seven Hills\"?",
                "options": ["Rome", "Istanbul", "Athens", "Lisbon"],
                "answer": 0,
            },
            {
                "q": "A bus starts from point A and goes 4 km north, 3 km east, 2 km south, and 3 km west. How far is it from the starting point?",
                "options": ["2 km", "3 km", "4 km", "1 km"],
                "answer": 0,
            },
            {
                "q": "Icy, cold, and vast —Which desert claims the title of the largest on Earth despite no sand in sight?",
                "options": ["Sahara", "Arabian", "Gobi", "Antarctica"],
                "answer": 3,
            },
            {
                "q": "\"The Joy of Flying\" is associated with:",
                "options": ["Air India", "Jet Airways", "Lufthansa", "Emirates"],
                "answer": 1,
            },
            {
                "q": "\"I'm Lovin' It\" was first launched as a global campaign in which year?",
                "options": ["2001", "2003", "2005", "2007"],
                "answer": 1,
            },
            {
                "q": "Who is the only athlete to have won Olympic gold medals in both the 100m and 200m events in three consecutive Olympics?",
                "options": ["Carl Lewis", "Usain Bolt", "Jesse Owens", "Florence Griffith-Joyner"],
                "answer": 1,
            },
        ]

    def _build_mystery_cards(self):
        # Spin wheel mystery effects - 5 specific options
        return [
            {"type": "move", "steps": 3, "text": "Advance 3 spaces", "color": (76, 175, 80)},
            {"type": "move", "steps": -2, "text": "Go back 2 spaces", "color": (244, 67, 54)},
            {"type": "go_to_free_parking", "text": "Go to free parking", "color": (33, 150, 243)},
            {"type": "go_to_society_penalty", "text": "Go to society penalty", "color": (156, 39, 176)},
            {"type": "no_rent", "text": "No rent next turn", "color": (255, 193, 7)},
        ]

    def _build_property_data(self):
        # Property mapping per provided board order (prices in rupees)
        return {
            1: {"name": "Electric Cars", "price": 3_000_000, "rent": 500_000, "color": (255, 140, 0), "description": "Next-gen EV venture"},
            3: {"name": "Snacks & Beverages", "price": 2_500_000, "rent": 500_000, "color": (255, 140, 0), "description": "FMCG snacks and drinks"},
            5: {"name": "Dairy Products", "price": 2_000_000, "rent": 500_000, "color": (255, 140, 0), "description": "Milk and dairy brand"},
            7: {"name": "Wearable Tech", "price": 3_000_000, "rent": 1_000_000, "color": (34, 139, 34), "description": "Smart wearables and health"},
            9: {"name": "Smart Home Devices", "price": 3_500_000, "rent": 1_000_000, "color": (34, 139, 34), "description": "IoT devices for home"},
            11: {"name": "Eco Headphones", "price": 2_500_000, "rent": 1_000_000, "color": (34, 139, 34), "description": "Sustainable audio gear"},
            13: {"name": "Fashion Tech", "price": 2_500_000, "rent": 500_000, "color": (30, 144, 255), "description": "Tech-infused apparel"},
            15: {"name": "Luxury Accessories", "price": 3_000_000, "rent": 1_000_000, "color": (30, 144, 255), "description": "Premium accessories"},
            17: {"name": "Sustainable Apparel", "price": 2_000_000, "rent": 500_000, "color": (30, 144, 255), "description": "Eco-friendly clothing"},
            19: {"name": "OTT Platforms", "price": 3_000_000, "rent": 1_000_000, "color": (220, 20, 60), "description": "Streaming services"},
            21: {"name": "Fast Food Chains", "price": 2_000_000, "rent": 500_000, "color": (220, 20, 60), "description": "Quick service restaurants"},
            23: {"name": "Motorbikes", "price": 2_500_000, "rent": 1_000_000, "color": (220, 20, 60), "description": "Two-wheeler brand"},
        }

    def _try_read_properties_from_image(self):
        """Try to read property names from the board image using OCR or pattern matching"""
        try:
            # This is a placeholder for future OCR implementation
            # For now, we'll use the default property data
            # In the future, this could use pytesseract or similar OCR libraries
            # to read property names directly from the board image
            pass
        except Exception as e:
            print(f"Could not read properties from image: {e}")
            # Fall back to default property data

    def _compute_layout_rects(self):
        # Board centered horizontally considering right sidebar and header space
        HEADER_H = 90  # Height of the title header
        max_board_h = self.screen_h - UI_H - HEADER_H - 2 * MARGIN
        max_board_w = self.screen_w - SIDEBAR_W - 3 * MARGIN
        size = min(max_board_h, max_board_w)
        # center board in remaining space (left area)
        left_area_w = self.screen_w - SIDEBAR_W - 2 * MARGIN
        board_x = MARGIN + (left_area_w - size) // 2
        board_y = HEADER_H + MARGIN  # Start below the header
        board_rect = pygame.Rect(board_x, board_y, size, size)
        sidebar_x = self.screen_w - SIDEBAR_W - MARGIN
        sidebar_y = board_y
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, SIDEBAR_W, size)
        return board_rect, sidebar_rect

    def _compute_positions(self):
        cells = 7
        br = self.board_rect
        cell_w = br.width // cells
        cell_h = br.height // cells
        self.positions = []
        
        # Counter-clockwise path starting from GO (bottom-left)
        # Bottom row: GO (0) to right edge (1-6)
        for i in range(cells):
            self.positions.append((br.x + i * cell_w + cell_w // 2, br.y + br.height - cell_h // 2))
        
        # Right edge: bottom-right (7) to top-right (8-12)
        for i in range(1, cells):
            self.positions.append((br.x + br.width - cell_w // 2, br.y + (cells - 1 - i) * cell_h + cell_h // 2))
        
        # Top row: top-right (13) to left (14-19)
        for i in range(cells - 2, -1, -1):
            self.positions.append((br.x + i * cell_w + cell_w // 2, br.y + cell_h // 2))
        
        # Left edge: top-left (20) to bottom-left (21-23)
        for i in range(1, cells - 1):
            self.positions.append((br.x + cell_w // 2, br.y + i * cell_h + cell_h // 2))

    def run(self):
        while True:
            self.clock.tick(FPS)
            if not self._handle_events():
                break
            self._update()
            self._draw()
        pygame.quit()
        sys.exit(0)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                # Recreate window with new size and recompute layout/positions
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_w, self.screen_h = self.screen.get_size()
                self.board_rect, self.sidebar_rect = self._compute_layout_rects()
                self._compute_positions()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_chance:
                        self.show_chance = False
                        self.chance_feedback = None
                    elif self.show_chance_confirm:
                        self.show_chance_confirm = False
                    elif self.show_mystery:
                        self.show_mystery = False
                        self.mystery_feedback = None
                    elif self.show_sell_property:
                        self.show_sell_property = False
                        self.sell_property_feedback = None
                    elif self.show_trading:
                        self._cancel_trading()
                    else:
                        return False
                if event.key == pygame.K_r and not self.moving and not self.show_chance and not self.show_chance_confirm and not self.show_mystery and not self.show_trading:
                    self.roll_dice()
                if event.key == pygame.K_b and not self.moving and not self.show_chance and not self.show_chance_confirm and not self.show_mystery and not self.show_trading:
                    self.buy_current()
                if event.key == pygame.K_e and not self.moving and not self.show_chance and not self.show_chance_confirm and not self.show_mystery and not self.show_trading:
                    self.next_turn()
                if event.key == pygame.K_s and not self.moving and not self.show_chance and not self.show_chance_confirm and not self.show_mystery and not self.show_trading:
                    self._show_sell_property()
                if event.key == pygame.K_t and not self.moving and not self.show_chance and not self.show_chance_confirm and not self.show_mystery and not self.show_trading:
                    self._start_trading()
                if event.key == pygame.K_u and not self.moving and not self.show_chance and not self.show_chance_confirm and not self.show_mystery and not self.show_trading:
                    self.undo_move()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(event.pos)
        return True

    def _handle_mouse_click(self, pos):
        # Prefer last drawn clickable areas (buttons, money controls, chance/mystery options)
        for rect, action in getattr(self, "click_areas", []):
            if rect.collidepoint(pos):
                try:
                    # Play click sound
                    self._play_sound('click')
                    action()
                except Exception:
                    pass
                return
        # Fallback to base buttons
        for label, rect, action in self._ui_buttons():
            if rect.collidepoint(pos):
                # Play click sound
                self._play_sound('click')
                action()
                return

        if self.chance_feedback or self.mystery_feedback or self.sell_property_feedback:
            self.chance_feedback = None
            self.mystery_feedback = None
            self.sell_property_feedback = None
            return

    def roll_dice(self):
        # Save state before rolling dice
        self._save_state()
        # Enhanced randomization for better dice distribution
        # Use multiple entropy sources for better randomness
        current_time = time.time()
        random.seed(int(current_time * 1000000) % 2**32)  # Microsecond precision seeding
        
        # Generate multiple random numbers and pick the most varied one
        dice_rolls = []
        for _ in range(3):  # Generate 3 potential rolls
            dice_rolls.append(random.randint(1, 6))
        
        # Add some additional entropy from system state
        entropy_bonus = (hash(str(current_time)) + len(self.game_history)) % 6 + 1
        
        # Use weighted selection to avoid consecutive similar numbers
        if hasattr(self, 'last_dice_roll'):
            # Avoid repeating the same number
            available_rolls = [r for r in dice_rolls if r != self.last_dice_roll]
            if available_rolls:
                d = random.choice(available_rolls)
            else:
                d = random.choice(dice_rolls)
        else:
            d = random.choice(dice_rolls)
        
        # Occasionally use entropy bonus for extra variation
        if random.random() < 0.3:  # 30% chance to use entropy bonus
            d = entropy_bonus
        
        # Store last roll to avoid immediate repetition
        self.last_dice_roll = d
        
        # Play dice roll sound
        self._play_sound('dice')
        
        # Log dice roll event
        self.log_streamlit_event(f"{self.teams[self.current_idx].name} rolled a {d}")
        
        self.move_steps = d
        self.move_progress = 0.0
        self.moving = True
        # prepare first segment
        team = self.teams[self.current_idx]
        self.from_pos_idx = team.pos
        self.to_pos_idx = (team.pos + 1) % BOARD_SPACES

    def _update(self):
        if self.moving:
            # Slow smooth interpolation
            self.move_progress += 0.06
            if self.move_progress >= 1.0:
                self.move_progress = 0.0
                # commit the step
                team = self.teams[self.current_idx]
                # Detect wrap-around to apply GO bonus
                if self.to_pos_idx < self.from_pos_idx:
                    team.balance += 2_000_000
                team.pos = self.to_pos_idx
                self._record_trail()
                
                # Play movement sound
                self._play_sound('move')
                
                self.move_steps -= 1
                if self.move_steps <= 0:
                    self.moving = False
                    # Check tile
                    if team.pos in CHANCE_TILES:
                        self.show_chance_confirm = True
                    elif team.pos in MYSTERY_TILES:
                        self._trigger_mystery()
                    elif team.pos == 6:
                        # Society Penalty: Pay 1M and skip next turn
                        team.balance -= 1_000_000
                        self.skip_next_turn[team.team_id] = True
                        self.mystery_feedback = "Society Penalty: Lost ₹1.0M, skip next turn"
                        self.feedback_timer = 120  # ~2s
                    elif team.pos == 12:
                        # Free Parking: no action
                        pass
                    elif team.pos == 18:
                        # Event Penalty – ₹1.5M
                        team.balance -= 1_500_000
                        self.mystery_feedback = "Event Penalty: Lost ₹1.5M"
                        self.feedback_timer = 120
                    # No auto-advance; user ends turn
                else:
                    # prepare next segment
                    self.from_pos_idx = team.pos
                    self.to_pos_idx = (team.pos + 1) % BOARD_SPACES
        
        # Update spin wheel animation
        self._update_spin_wheel()
        
        # Auto-apply mystery after spin completes
        if self.selected_mystery and not self.spinning and self.overlay_timer > 0:
            self.overlay_timer -= 1
            if self.overlay_timer <= 0:
                self._apply_mystery()
        
        # Update feedback timer
        if (self.chance_feedback or self.mystery_feedback or self.sell_property_feedback) and self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer <= 0:
                self.chance_feedback = None
                self.mystery_feedback = None
                self.sell_property_feedback = None
        
        # Check Streamlit commands and actions
        self.check_streamlit_commands()
        self.check_streamlit_player_actions()
        
        # Save state for Streamlit
        self.save_streamlit_state()

    def _record_trail(self):
        team = self.teams[self.current_idx]
        trail = self.token_trail[team.team_id]
        trail.append(team.pos)
        if len(trail) > 15:
            trail.pop(0)

    def undo_move(self):
        """Undo the last move made in the game"""
        if self._undo_state():
            # Clear any active overlays when undoing
            self.show_chance = False
            self.show_chance_confirm = False
            self.show_mystery = False
            self.chance_feedback = None
            self.mystery_feedback = None
            self.feedback_timer = 0
            self.overlay_timer = 0
            # Stop any ongoing movement
            self.moving = False
            self.move_steps = 0
            self.move_progress = 0.0
            self.from_pos_idx = None
            self.to_pos_idx = None

    def next_turn(self):
        # Save state before advancing turn
        self._save_state()
        # advance to next, honoring skip flags
        attempts = 0
        while attempts < len(self.teams):
            self.current_idx = (self.current_idx + 1) % len(self.teams)
            team = self.teams[self.current_idx]
            if self.skip_next_turn.get(team.team_id):
                self.skip_next_turn[team.team_id] = False
                attempts += 1
                continue
            break
        
        # Log turn advancement
        self.log_streamlit_event(f"Turn advanced to {self.teams[self.current_idx].name}")

    def can_buy(self, team):
        space = team.pos % BOARD_SPACES
        # Disallow buying on GO, special tiles and free parking / penalty tiles
        if space in {0, 6, 12, 18} or space in CHANCE_TILES or space in MYSTERY_TILES:
            return False
        if self.properties[space]["owner"] is not None:
            return False
        return True

    def buy_current(self):
        team = self.teams[self.current_idx]
        if not self.can_buy(team):
            return
        # Save state before buying property
        self._save_state()
        self.properties[team.pos % BOARD_SPACES]["owner"] = team.team_id
        
        # Play property purchase sound
        self._play_sound('purchase')
        
        # Log property purchase event
        prop_name = self.property_data.get(team.pos, {}).get('name', f'Property {team.pos}')
        self.log_streamlit_event(f"{team.name} bought {prop_name}")

    def _trigger_chance(self):
        # Choose a random chance question that hasn't been used recently
        available_questions = [card for card in self.chance_cards if card not in self.used_chance_questions]
        if not available_questions:
            # If all questions have been used, reset the list
            self.used_chance_questions = []
            available_questions = self.chance_cards.copy()
        
        self.chance_card = random.choice(available_questions)
        self.used_chance_questions.append(self.chance_card)
        self.show_chance = True
        self.chance_feedback = None
        self.overlay_timer = 300  # ~5s

    def _draw_chance_confirm_overlay(self):
        """Draw the chance confirmation popup"""
        if not self.show_chance_confirm:
            return
        
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        self.screen.blit(overlay, (0,0))
        
        br = self.board_rect
        box_w = 400
        box_h = 200
        box = pygame.Rect(0, 0, box_w, box_h)
        box.center = br.center
        
        # Box background
        pygame.draw.rect(self.screen, (255,255,255), box, border_radius=12)
        pygame.draw.rect(self.screen, (0,0,0), box, 3, border_radius=12)
        
        # Title
        title_text = self.font.render("🎲 CHANCE SPACE", True, (0,0,0))
        title_rect = title_text.get_rect(center=(box.centerx, box.y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Question
        question_text = self.font.render("Do you want to take the chance?", True, (0,0,0))
        question_rect = question_text.get_rect(center=(box.centerx, box.y + 70))
        self.screen.blit(question_text, question_rect)
        
        # Yes button
        yes_btn = pygame.Rect(box.x + 50, box.y + 110, 100, 40)
        pygame.draw.rect(self.screen, (34,139,34), yes_btn, border_radius=8)
        pygame.draw.rect(self.screen, (255,255,255), yes_btn, 2, border_radius=8)
        yes_text = self.font.render("YES", True, (255,255,255))
        self._blit_center_surface(yes_text, yes_btn)
        self.click_areas.append((yes_btn, self._confirm_chance_yes))
        
        # No button
        no_btn = pygame.Rect(box.x + 250, box.y + 110, 100, 40)
        pygame.draw.rect(self.screen, (220,20,60), no_btn, border_radius=8)
        pygame.draw.rect(self.screen, (255,255,255), no_btn, 2, border_radius=8)
        no_text = self.font.render("NO", True, (255,255,255))
        self._blit_center_surface(no_text, no_btn)
        self.click_areas.append((no_btn, self._confirm_chance_no))

    def _confirm_chance_yes(self):
        """Player chose to take the chance"""
        self.show_chance_confirm = False
        self._trigger_chance()
    
    def _confirm_chance_no(self):
        """Player chose to skip the chance"""
        self.show_chance_confirm = False
        # No penalty for skipping chance
    
    def _test_chance(self):
        """Test method to manually trigger chance"""
        self.show_chance_confirm = True
    
    def _test_mystery(self):
        """Test method to manually trigger mystery"""
        self._trigger_mystery()
    
    def _test_sound(self):
        """Test method to check if sounds are working"""
        print("Testing all sounds...")
        for sound_name in ['dice', 'move', 'spin', 'purchase', 'click']:
            print(f"Testing {sound_name} sound...")
            self._play_sound(sound_name)
            pygame.time.wait(200)  # Wait 200ms between sounds
        print("Sound test completed!")
    
    def _test_randomization(self):
        # Test method to check randomization - run 10 spins and show results
        print("Testing mystery wheel randomization...")
        results = []
        for i in range(10):
            # Simulate a spin without the full animation
            num_cards = len(self.mystery_cards)
            angle_per_segment = 360 / num_cards
            
            # Choose random segment
            available_segments = list(range(num_cards))
            for recent_result in self.recent_mystery_results:
                if recent_result in available_segments:
                    available_segments.remove(recent_result)
            
            if not available_segments:
                available_segments = list(range(num_cards))
                self.recent_mystery_results = []
            
            target_segment = random.choice(available_segments)
            self.recent_mystery_results.append(target_segment)
            if len(self.recent_mystery_results) > self.max_recent_results:
                self.recent_mystery_results.pop(0)
            
            results.append(self.mystery_cards[target_segment]["text"])
        
        print("Last 10 mystery results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}: {result}")
        
        # Count occurrences
        from collections import Counter
        counts = Counter(results)
        print("Distribution:")
        for text, count in counts.items():
            print(f"  {text}: {count} times")

    def _save_state(self):
        """Save current game state to history for undo functionality"""
        state = {
            'teams': [
                {
                    'team_id': team.team_id,
                    'name': team.name,
                    'color': team.color,
                    'balance': team.balance,
                    'pos': team.pos
                } for team in self.teams
            ],
            'current_idx': self.current_idx,
            'properties': [prop.copy() for prop in self.properties],
            'moving': self.moving,
            'move_steps': self.move_steps,
            'move_progress': self.move_progress,
            'from_pos_idx': self.from_pos_idx,
            'to_pos_idx': self.to_pos_idx,
            'token_trail': {k: v.copy() for k, v in self.token_trail.items()},
            'skip_next_turn': self.skip_next_turn.copy(),
            'show_chance': self.show_chance,
            'chance_card': self.chance_card,
            'chance_feedback': self.chance_feedback,
            'show_chance_confirm': self.show_chance_confirm,
            'feedback_timer': self.feedback_timer,
            'show_mystery': self.show_mystery,
            'mystery_card': self.mystery_card,
            'mystery_feedback': self.mystery_feedback,
            'overlay_timer': self.overlay_timer,
            'show_sell_property': self.show_sell_property,
            'sell_property_feedback': self.sell_property_feedback,
            'spinning': self.spinning,
            'spin_angle': self.spin_angle,
            'spin_speed': self.spin_speed,
            'spin_target_angle': self.spin_target_angle,
            'spin_duration': self.spin_duration,
            'spin_progress': self.spin_progress,
            'selected_mystery': self.selected_mystery,
            'used_mysteries': self.used_mysteries.copy(),
            'used_chance_questions': self.used_chance_questions.copy()
        }
        
        # Add to history and limit size
        self.game_history.append(state)
        if len(self.game_history) > self.max_history_size:
            self.game_history.pop(0)

    def _undo_state(self):
        """Restore previous game state from history"""
        if not self.game_history:
            return False
        
        state = self.game_history.pop()
        
        # Restore teams
        for i, team_data in enumerate(state['teams']):
            self.teams[i].team_id = team_data['team_id']
            self.teams[i].name = team_data['name']
            self.teams[i].color = team_data['color']
            self.teams[i].balance = team_data['balance']
            self.teams[i].pos = team_data['pos']
        
        # Restore game state
        self.current_idx = state['current_idx']
        self.properties = state['properties']
        self.moving = state['moving']
        self.move_steps = state['move_steps']
        self.move_progress = state['move_progress']
        self.from_pos_idx = state['from_pos_idx']
        self.to_pos_idx = state['to_pos_idx']
        self.token_trail = state['token_trail']
        self.skip_next_turn = state['skip_next_turn']
        self.show_chance = state['show_chance']
        self.chance_card = state['chance_card']
        self.chance_feedback = state['chance_feedback']
        self.show_chance_confirm = state.get('show_chance_confirm', False)
        self.feedback_timer = state['feedback_timer']
        self.show_mystery = state['show_mystery']
        self.mystery_card = state['mystery_card']
        self.mystery_feedback = state['mystery_feedback']
        self.overlay_timer = state['overlay_timer']
        self.show_sell_property = state['show_sell_property']
        self.sell_property_feedback = state['sell_property_feedback']
        self.spinning = state.get('spinning', False)
        self.spin_angle = state.get('spin_angle', 0)
        self.spin_speed = state.get('spin_speed', 0)
        self.spin_target_angle = state.get('spin_target_angle', 0)
        self.spin_duration = state.get('spin_duration', 0)
        self.spin_progress = state.get('spin_progress', 0)
        self.selected_mystery = state.get('selected_mystery', None)
        self.used_mysteries = state.get('used_mysteries', [])
        self.used_chance_questions = state.get('used_chance_questions', [])
        
        return True

    def _reset_game(self):
        # Reset all game state
        for team in self.teams:
            team.pos = 0
            team.balance = 10_000_000
        self.current_idx = 0
        self.moving = False
        self.move_steps = 0
        self.move_progress = 0.0
        self.from_pos_idx = None
        self.to_pos_idx = None
        self.token_trail = {t.team_id: [] for t in self.teams}
        self.show_chance = False
        self.chance_card = None
        self.chance_feedback = None
        self.show_chance_confirm = False
        self.feedback_timer = 0
        self.show_mystery = False
        self.mystery_card = None
        self.mystery_feedback = None
        self.spinning = False
        self.spin_angle = 0
        self.spin_speed = 0
        self.spin_target_angle = 0
        self.spin_duration = 0
        self.spin_progress = 0
        self.selected_mystery = None
        self.used_mysteries = []
        self.used_chance_questions = []
        self.recent_mystery_results = []
        # Reset all properties
        for prop in self.properties:
            prop["owner"] = None
        # Clear history on reset
        self.game_history = []
        # Reset dice tracking
        self.last_dice_roll = None

    def _trigger_mystery(self):
        self.show_mystery = True
        self.mystery_feedback = None
        self.overlay_timer = 300  # ~5s
        self._start_spin_wheel()

    def _draw_board(self):
        # Background with gradient effect
        self.screen.fill((245, 247, 251))
        
        # Add subtle background pattern
        for i in range(0, self.screen_w, 40):
            for j in range(0, self.screen_h, 40):
                if (i + j) % 80 == 0:
                    pygame.draw.circle(self.screen, (240, 242, 246), (i, j), 2)
        
        br = self.board_rect
        
        # Board shadow
        shadow_rect = br.inflate(20, 20)
        shadow_rect.x += 10
        shadow_rect.y += 10
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=16)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Board image area with enhanced border
        pygame.draw.rect(self.screen, (255, 255, 255), br, border_radius=12)
        if self.board_image_original is not None:
            if (self.board_image_scaled is None) or (self.board_image_scaled.get_size() != (br.width, br.height)):
                self.board_image_scaled = pygame.transform.smoothscale(self.board_image_original, (br.width, br.height))
            self.screen.blit(self.board_image_scaled, br)
        
        # Enhanced border with multiple layers
        pygame.draw.rect(self.screen, (34, 34, 34), br, 8, border_radius=12)
        pygame.draw.rect(self.screen, (183, 28, 28), br, 3, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 0), br, 1, border_radius=12)
        
        # Debug labels removed - tiles are now clean without numbering

    def _draw_houses(self):
        cells = 7
        cell_w = self.board_rect.width // cells
        cell_h = self.board_rect.height // cells
        edge_offset = int(min(cell_w, cell_h) * 0.30)
        tangent_offset = 10
        for p in self.properties:
            owner = p["owner"]
            if not owner:
                continue
            color = next(t.color for t in self.teams if t.team_id == owner)
            x, y = self.positions[p["index"]]
            side = self._get_board_side(p["index"]) 
            hx, hy = x, y
            if side == 'bottom':
                hy = y - edge_offset; hx = x + tangent_offset
            elif side == 'right':
                hx = x - edge_offset; hy = y - tangent_offset
            elif side == 'top':
                hy = y + edge_offset; hx = x - tangent_offset
            else:
                hx = x + edge_offset; hy = y + tangent_offset
            self._draw_house_icon(hx, hy, color)

    def _get_board_side(self, idx):
        if 0 <= idx <= 6:
            return 'bottom'
        if 7 <= idx <= 12:
            return 'right'
        if 13 <= idx <= 19:
            return 'top'
        return 'left'

    def _draw_house_icon(self, cx, by, color):
        scale = max(14, self.board_rect.width // 55)
        body_w = int(scale * 1.2)
        body_h = int(scale * 0.8)
        roof_h = int(scale * 0.6)
        left = int(cx - body_w / 2)
        top = int(by - body_h)
        # shadow
        shadow = pygame.Surface((body_w+6, body_h+6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,90), shadow.get_rect())
        self.screen.blit(shadow, (left-3, top + body_h - 4))
        # body and roof
        pygame.draw.rect(self.screen, color, (left, top, body_w, body_h))
        pygame.draw.rect(self.screen, (34,34,34), (left, top, body_w, body_h), 1)
        points = [(cx, top - roof_h), (left - 1, top), (left + body_w + 1, top)]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, (34,34,34), points, 1)
        # door
        door_w = max(4, int(body_w * 0.26))
        door_h = max(5, int(body_h * 0.6))
        door_left = int(cx - door_w / 2)
        door_top = int(top + body_h - door_h)
        pygame.draw.rect(self.screen, (255,255,255), (door_left, door_top, door_w, door_h))

    def _draw_tokens(self):
        # animated tokens with shadow, rim, and shine
        for idx, team in enumerate(self.teams):
            # Interpolate current player's token if moving
            if self.moving and team is self.teams[self.current_idx] and self.from_pos_idx is not None:
                fx, fy = self.positions[self.from_pos_idx]
                tx, ty = self.positions[self.to_pos_idx]
                x = fx + (tx - fx) * self._ease_in_out(self.move_progress)
                y = fy + (ty - fy) * self._ease_in_out(self.move_progress)
            else:
                x, y = self.positions[team.pos]
            bob = math.sin(pygame.time.get_ticks()/300.0 + idx) * 3
            # shadow
            shadow_rect = pygame.Rect(0,0,34,14)
            shadow_rect.center = (int(x + idx*6), int(y + idx*6 + 16))
            pygame.draw.ellipse(self.screen, (0,0,0,120), shadow_rect)
            # body
            center = (int(x + idx*6), int(y + idx*6 + bob))
            pygame.draw.circle(self.screen, team.color, center, 18)
            pygame.draw.circle(self.screen, (30,30,30), center, 18, 2)  # rim
            # shine
            pygame.draw.circle(self.screen, (255,255,255,40), (center[0]-6, center[1]-8), 8)
            # label
            label = self.font.render(team.team_id, True, (255,255,255))
            self.screen.blit(label, (center[0] - label.get_width()/2, center[1] - label.get_height()/2))

    def _ease_in_out(self, t):
        # smoothstep-like easing
        return t * t * (3 - 2 * t)

    def _ui_buttons(self):
        y = self.board_rect.bottom + MARGIN
        btn_w = 160
        btn_h = 46
        gap = 16
        buttons = []
        labels_actions = [
            ("🎲 Roll Dice (R)", self.roll_dice),
            ("🏠 Buy (B)", self.buy_current),
            ("💰 Sell Property (S)", self._show_sell_property),
            ("🤝 Start Trading (T)", self._start_trading),
            ("⏭️ End Turn (E)", self.next_turn),
            ("↶ Undo (U)", self.undo_move),
            ("🎯 Test Chance", self._test_chance),
            ("🔮 Test Mystery", self._test_mystery),
            ("🎲 Test Random", self._test_randomization),
            ("🔊 Test Sound", self._test_sound),
            ("🔄 Reset Game", self._reset_game),
        ]
        for i, (label, action) in enumerate(labels_actions):
            rect = pygame.Rect(MARGIN + i*(btn_w+gap), y, btn_w, btn_h)
            buttons.append((label, rect, action))
        return buttons

    def _draw_ui(self):
        # Reset clickable areas for this frame
        self.click_areas = []
        
        # Game Title at the top with enhanced styling
        title_rect = pygame.Rect(0, 0, self.screen_w, 90)  # Increased height for better spacing
        pygame.draw.rect(self.screen, (183, 28, 28), title_rect)
        
        # Enhanced title shadow effect
        title_shadow = self.title_font.render("ARTHVIDYA PRESENTS", True, (0, 0, 0))
        self.screen.blit(title_shadow, (MARGIN + 3, 15))
        
        # Main title with enhanced positioning
        title_text = self.title_font.render("ARTHVIDYA PRESENTS", True, (255, 255, 255))
        self.screen.blit(title_text, (MARGIN, 12))
        
        # Subtitle with better positioning
        subtitle_text = self.subtitle_font.render("MARKETERS MONOPOLY", True, (255, 215, 0))
        self.screen.blit(subtitle_text, (MARGIN, 58))
        
        # Enhanced decorative elements
        pygame.draw.line(self.screen, (255, 215, 0), (MARGIN, 85), (self.screen_w - MARGIN, 85), 4)
        
        # Additional decorative accent
        pygame.draw.line(self.screen, (255, 255, 255), (MARGIN, 87), (self.screen_w - MARGIN, 87), 1)
        
        # Bottom bar background with enhanced styling
        bar_rect = pygame.Rect(0, self.board_rect.bottom, self.screen_w, UI_H)
        pygame.draw.rect(self.screen, (255,255,255), bar_rect)
        pygame.draw.rect(self.screen, (230,232,239), bar_rect, 2)
        
        # Buttons row with enhanced styling
        for label, rect, action in self._ui_buttons():
            # Button shadow
            shadow_rect = rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, (0, 0, 0, 60), shadow_rect, border_radius=10)
            
            # Button background with gradient effect
            pygame.draw.rect(self.screen, (183,28,28), rect, border_radius=10)
            pygame.draw.rect(self.screen, (255,255,255), rect, 2, border_radius=10)
            
            # Hover effect (simple highlight)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (200, 50, 50), rect, border_radius=10)
            
            # Draw button icon based on label
            self._draw_button_icon(label, rect)
            
            text = self.font.render(label, True, (255,255,255))
            self._blit_center_surface(text, rect)
            self.click_areas.append((rect, action))
        # Sidebar - Money Tracker with enhanced styling
        sbr = self.sidebar_rect
        
        # Sidebar shadow
        shadow_rect = sbr.copy()
        shadow_rect.x += 8
        shadow_rect.y += 8
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), shadow_surface.get_rect(), border_radius=12)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Sidebar background with gradient effect
        pygame.draw.rect(self.screen, (255,255,255), sbr, border_radius=12)
        pygame.draw.rect(self.screen, (183, 28, 28), sbr, 3, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 0), sbr, 1, border_radius=12)
        
        # Enhanced title with background
        title_bg = pygame.Rect(sbr.x + 8, sbr.y + 8, sbr.width - 16, 40)
        pygame.draw.rect(self.screen, (183, 28, 28), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), title_bg, 2, border_radius=8)
        
        title = self.money_font.render("$ MONEY TRACKER", True, (255,255,255))
        self.screen.blit(title, (sbr.x + 16, sbr.y + 16))
        y = sbr.y + 52
        for i, team in enumerate(self.teams):
            # Enhanced team row with better styling
            row_rect = pygame.Rect(sbr.x + 12, y - 6, sbr.width - 24, 52)
            
            # Row shadow
            shadow_rect = row_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(self.screen, (0, 0, 0, 20), shadow_rect, border_radius=8)
            
            # Row background with enhanced borders
            if i == self.current_idx:
                # Active team - highlighted
                pygame.draw.rect(self.screen, (255, 235, 238), row_rect, border_radius=8)
                pygame.draw.rect(self.screen, (183, 28, 28), row_rect, 3, border_radius=8)
                pygame.draw.rect(self.screen, (255, 215, 0), row_rect, 1, border_radius=8)
            else:
                # Inactive team
                pygame.draw.rect(self.screen, (248, 250, 252), row_rect, border_radius=8)
                pygame.draw.rect(self.screen, (183, 28, 28), row_rect, 2, border_radius=8)
            
            # Team info with enhanced styling
            name = self.font.render(f"* {team.team_id} — {team.name}", True, team.color)
            self.screen.blit(name, (sbr.x + 20, y))
            y += 20
            
            # Balance with currency symbol and better formatting
            # Try multiple rupee symbol representations for better compatibility
            rupee_symbol = "₹"  # Unicode rupee symbol
            try:
                bal = self.font.render(f"$ {rupee_symbol}{team.balance/1_000_000:.1f}M", True, (20,20,20))
            except:
                # Fallback to "Rs." if rupee symbol fails
                bal = self.font.render(f"$ Rs. {team.balance/1_000_000:.1f}M", True, (20,20,20))
            self.screen.blit(bal, (sbr.x + 20, y))
            
            # Enhanced money controls with better styling
            bx = sbr.x + sbr.width - 3*76 - 30
            for label, delta in [("+0.5M", 500_000), ("+1M", 1_000_000), ("-0.5M", -500_000)]:
                rect = pygame.Rect(bx, y - 4, 70, 26)
                
                # Button shadow
                shadow_btn = rect.copy()
                shadow_btn.x += 1
                shadow_btn.y += 1
                pygame.draw.rect(self.screen, (0, 0, 0, 30), shadow_btn, border_radius=6)
                
                # Button background with enhanced borders
                pygame.draw.rect(self.screen, (247, 249, 252), rect, border_radius=6)
                pygame.draw.rect(self.screen, (183, 28, 28), rect, 2, border_radius=6)
                pygame.draw.rect(self.screen, (255, 215, 0), rect, 1, border_radius=6)
                
                # Hover effect
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (220, 240, 255), rect, border_radius=6)
                
                t = self.font.render(label, True, (20,20,20))
                self._blit_center_surface(t, rect)
                
                idx = i
                def act(ix=idx, d=delta):
                    return lambda: self._adjust_balance(ix, d)
                self.click_areas.append((rect, act()))
                bx += 76
            y += 40

    def _adjust_balance(self, team_index, delta):
        try:
            # Save state before adjusting balance
            self._save_state()
            self.teams[team_index].balance += int(delta)
        except Exception:
            pass

    def _draw_chance_overlay(self):
        if not self.show_chance or not self.chance_card:
            return
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        self.screen.blit(overlay, (0,0))
        br = self.board_rect
        box_w = max(420, int(br.width * 0.78))
        box_h = 300
        box = pygame.Rect(0, 0, min(box_w, br.width - 20), min(box_h, br.height - 20))
        box.center = br.center
        
        # Enhanced box with shadow and borders
        shadow_rect = box.copy()
        shadow_rect.x += 8
        shadow_rect.y += 8
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect(), border_radius=16)
        self.screen.blit(shadow_surface, shadow_rect)
        
        pygame.draw.rect(self.screen, (255,255,255), box, border_radius=14)
        pygame.draw.rect(self.screen, (183, 28, 28), box, 4, border_radius=14)
        pygame.draw.rect(self.screen, (255, 215, 0), box, 2, border_radius=14)
        
        # Enhanced title with background
        title_bg = pygame.Rect(box.x + 10, box.y + 10, box.width - 20, 40)
        pygame.draw.rect(self.screen, (183, 28, 28), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), title_bg, 2, border_radius=8)
        
        qsurf = self.big_font.render("* CHANCE", True, (255,255,255))
        self.screen.blit(qsurf, (box.x+20, box.y+16))
        lines = self._wrap_text(self.chance_card["q"], self.font, box.width-40)
        yy = box.y + 56
        for ln in lines:
            self.screen.blit(ln, (box.x+20, yy))
            yy += ln.get_height() + 6
        # Options
        opt_y = yy + 10
        for i, opt in enumerate(self.chance_card["options"]):
            opt_rect = pygame.Rect(box.x+20, opt_y, box.width-40, 34)
            pygame.draw.rect(self.screen, (247,249,252), opt_rect, border_radius=8)
            pygame.draw.rect(self.screen, (230,232,239), opt_rect, 1, border_radius=8)
            text = self.font.render(opt, True, (20,20,20))
            self._blit_center_surface(text, opt_rect)
            # Register clickable area to check answer and show feedback
            idx = i
            def check_answer(ix=idx):
                return lambda: self._check_chance_answer(ix)
            self.click_areas.append((opt_rect, check_answer()))
            opt_y += 42

    def _check_chance_answer(self, selected_index):
        # Save state before checking answer
        self._save_state()
        correct = selected_index == self.chance_card["answer"]
        if correct:
            self.chance_feedback = "Correct! 🎉"
        else:
            self.chance_feedback = "Incorrect ❌"
        self.feedback_timer = 120  # 2 seconds
        # Close overlay immediately to keep flow clear
        self.show_chance = False

    def _draw_property_card(self):
        # Show property card when player lands on a property
        team = self.teams[self.current_idx]
        if team.pos in self.property_data:
            prop = self.property_data[team.pos]
            owner = self.properties[team.pos]["owner"]
            
            # Calculate position below money tracker based on actual last row bottom
            # Anchor card to the bottom of the sidebar box
            desired_h = 300
            max_h = max(220, self.sidebar_rect.height - 24)  # ensure some padding
            card_h = min(desired_h, max_h)
            card_rect = pygame.Rect(self.sidebar_rect.x + 16, 0, self.sidebar_rect.width - 32, card_h)
            card_rect.bottom = self.sidebar_rect.bottom - 12
            
            # Enhanced shadow effect
            shadow_rect = card_rect.copy()
            shadow_rect.x += 6
            shadow_rect.y += 6
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 40), shadow_surface.get_rect(), border_radius=14)
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Background with enhanced borders
            pygame.draw.rect(self.screen, prop["color"], card_rect, border_radius=12)
            pygame.draw.rect(self.screen, (255, 255, 255), card_rect, 4, border_radius=12)
            pygame.draw.rect(self.screen, (183, 28, 28), card_rect, 2, border_radius=12)
            pygame.draw.rect(self.screen, (255, 215, 0), card_rect, 1, border_radius=12)
            
            inner = card_rect.inflate(-10, -10)
            pygame.draw.rect(self.screen, (255,255,255), inner, border_radius=10)
            pygame.draw.rect(self.screen, prop["color"], inner, 3, border_radius=10)
            
            # Enhanced property color bar with shadow
            color_bar = pygame.Rect(inner.x + 10, inner.y + 10, inner.width - 20, 12)
            pygame.draw.rect(self.screen, (0, 0, 0, 30), color_bar.inflate(2, 2), border_radius=6)
            pygame.draw.rect(self.screen, prop["color"], color_bar, border_radius=6)
            pygame.draw.rect(self.screen, (255, 215, 0), color_bar, 1, border_radius=6)
            
            # Property name with enhanced styling
            name = self.big_font.render(f"* {prop['name']}", True, (20, 20, 20))
            self.screen.blit(name, (inner.x + 15, inner.y + 30))
            
            # Price with icon
            price = self.font.render(f"$ Price: ₹{prop['price']/1_000_000:.1f}M", True, (20, 20, 20))
            self.screen.blit(price, (inner.x + 15, inner.y + 65))
            
            # Rent with icon
            rent = self.font.render(f"$ Rent: ₹{prop['rent']/1_000_000:.1f}M", True, (20, 20, 20))
            self.screen.blit(rent, (inner.x + 15, inner.y + 90))
            
            # Description
            desc_lines = self._wrap_text(prop["description"], self.font, inner.width - 30)
            desc_y = inner.y + 120
            for line in desc_lines:
                self.screen.blit(line, (inner.x + 15, desc_y))
                desc_y += line.get_height() + 4
            
            # Owner info with enhanced styling
            if owner:
                owner_team = next(t for t in self.teams if t.team_id == owner)
                owner_text = self.font.render(f"* Owner: {owner_team.name}", True, owner_team.color)
                self.screen.blit(owner_text, (inner.x + 15, desc_y + 10))
            else:
                owner_text = self.font.render("* Owner: None (Available for Purchase!)", True, (100, 100, 100))
                self.screen.blit(owner_text, (inner.x + 15, desc_y + 10))

    def _draw_mystery_overlay(self):
        if not self.show_mystery:
            return
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        self.screen.blit(overlay, (0,0))
        br = self.board_rect
        
        # Draw spin wheel - make it larger
        wheel_radius = min(200, br.width // 3, br.height // 3)
        wheel_center_x = br.centerx
        wheel_center_y = br.centery - 20
        
        # Draw wheel shadow
        shadow_offset = 8
        pygame.draw.circle(self.screen, (0, 0, 0, 60), 
                         (wheel_center_x + shadow_offset, wheel_center_y + shadow_offset), 
                         wheel_radius + 5)
        
        # Draw the spinning wheel
        self._draw_spin_wheel(wheel_center_x, wheel_center_y, wheel_radius)
        
        # Draw title
        title_text = self.big_font.render("* MYSTERY WHEEL", True, (255,255,255))
        title_rect = title_text.get_rect(center=(wheel_center_x, wheel_center_y - wheel_radius - 60))
        
        # Title background
        title_bg = title_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (128, 0, 128), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), title_bg, 2, border_radius=8)
        self.screen.blit(title_text, title_rect)
        
        # Show result if spin is complete
        if self.selected_mystery and not self.spinning:
            result_text = self.font.render(f"Result: {self.selected_mystery['text']}", True, (255, 255, 255))
            result_rect = result_text.get_rect(center=(wheel_center_x, wheel_center_y + wheel_radius + 40))
            
            # Result background
            result_bg = result_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, self.selected_mystery['color'], result_bg, border_radius=8)
            pygame.draw.rect(self.screen, (255, 215, 0), result_bg, 2, border_radius=8)
            self.screen.blit(result_text, result_rect)

    def _apply_mystery(self):
        # Save state before applying mystery
        self._save_state()
        card = self.mystery_card
        team = self.teams[self.current_idx]
        
        if card["type"] == "move":
            # Move relative steps, clamped within board using modulo
            steps = card["steps"]
            team.pos = (team.pos + steps) % BOARD_SPACES
            if steps > 0:
                self.mystery_feedback = f"Advanced {steps} spaces!"
            else:
                self.mystery_feedback = f"Went back {abs(steps)} spaces!"
        elif card["type"] == "go_to_free_parking":
            # Go to free parking (position 12)
            team.pos = 12
            self.mystery_feedback = "Moved to Free Parking!"
        elif card["type"] == "go_to_society_penalty":
            # Go to society penalty (position 6)
            team.pos = 6
            self.mystery_feedback = "Moved to Society Penalty!"
        elif card["type"] == "no_rent":
            # Set a flag for no rent next turn (this would need to be implemented in rent collection)
            self.mystery_feedback = "No rent next turn! (Note: Manual implementation needed)"
        
        self.feedback_timer = 120
        self.show_mystery = False
        self.selected_mystery = None

    def _start_spin_wheel(self):
        """Start the spin wheel animation"""
        self.spinning = True
        self.spin_angle = 0
        self.spin_speed = 30  # Initial spin speed
        
        # Play wheel spinning sound
        self._play_sound('spin')
        self.spin_duration = 240  # Frames to spin (4 seconds at 60fps)
        self.spin_progress = 0
        self.selected_mystery = None
        self.mystery_card = None  # Will be determined after spin completes
        
        # Calculate target angle to land on a specific segment
        num_cards = len(self.mystery_cards)
        angle_per_segment = 360 / num_cards
        
        # Choose a random segment to land on with anti-repetition logic
        # Avoid repeating recent results
        available_segments = list(range(num_cards))
        
        # Remove recently used segments from available options
        for recent_result in self.recent_mystery_results:
            if recent_result in available_segments:
                available_segments.remove(recent_result)
        
        # If all segments were recently used, reset the list
        if not available_segments:
            available_segments = list(range(num_cards))
            self.recent_mystery_results = []
        
        # Choose from available segments
        target_segment = random.choice(available_segments)
        
        # Add some randomness to the segment positioning to avoid always landing exactly in center
        # This adds a small random offset within the segment
        segment_offset = random.uniform(-angle_per_segment * 0.3, angle_per_segment * 0.3)
        
        # Calculate the angle needed to position that segment at the top (0 degrees)
        # We want the segment to be at 0 degrees when the wheel stops
        segment_center_angle = target_segment * angle_per_segment + (angle_per_segment / 2) + segment_offset
        
        # Add multiple full rotations for visual effect with more variation
        min_rotations = 5
        max_rotations = 10
        rotations = random.randint(min_rotations, max_rotations)
        
        # Add some additional random angle to make it more unpredictable
        extra_random_angle = random.uniform(0, 360)
        
        # Calculate final target angle
        # We need to rotate so that the segment ends up at 0 degrees
        self.spin_target_angle = rotations * 360 + (360 - segment_center_angle) + extra_random_angle
        
        # Store the target segment for debugging/verification
        self.target_segment = target_segment

    def _update_spin_wheel(self):
        """Update spin wheel animation"""
        if not self.spinning:
            return
            
        self.spin_progress += 1
        
        # Calculate progress ratio (0 to 1)
        progress_ratio = self.spin_progress / self.spin_duration
        
        # Use smooth easing function for natural deceleration
        if progress_ratio < 0.6:
            # Fast spin phase - constant speed
            current_speed = self.spin_speed
        elif progress_ratio < 0.85:
            # Gradual slowdown phase
            slowdown_factor = 1.0 - ((progress_ratio - 0.6) / 0.25)
            current_speed = self.spin_speed * slowdown_factor
        else:
            # Final slow phase - exponential decay
            remaining_progress = 1.0 - progress_ratio
            current_speed = self.spin_speed * (remaining_progress ** 3) * 2
        
        # Ensure minimum speed for smooth movement
        current_speed = max(current_speed, 0.5)
        
        # Update angle
        self.spin_angle += current_speed
        
        # Check if spin is complete
        if self.spin_progress >= self.spin_duration:
            self.spinning = False
            # Set exact target angle
            self.spin_angle = self.spin_target_angle
            
            # Determine which segment is under the arrow (at 0 degrees)
            self._determine_selected_mystery()
            
            # Auto-apply the mystery after a longer delay (4-5 seconds)
            self.overlay_timer = 300  # 5 seconds delay at 60fps

    def _determine_selected_mystery(self):
        """Determine which mystery segment is under the arrow (at 0 degrees)"""
        num_cards = len(self.mystery_cards)
        angle_per_segment = 360 / num_cards
        
        # Normalize the final angle to 0-360 range
        final_angle = self.spin_angle % 360
        
        # The arrow points to 0 degrees (top of the wheel)
        # We need to find which segment is currently at the top (0 degrees)
        # Since segments rotate with the wheel, we need to find which segment's center
        # is closest to the 0 degree position after rotation
        
        # Find which segment is closest to 0 degrees (top)
        min_distance = float('inf')
        selected_index = 0
        
        # Debug: print segment positions
        segment_positions = []
        
        for i in range(num_cards):
            # Calculate where this segment's center is after rotation
            segment_center = (i * angle_per_segment + final_angle) % 360
            
            # Calculate distance from 0 degrees (considering wraparound)
            distance = min(segment_center, 360 - segment_center)
            
            segment_positions.append((i, segment_center, distance, self.mystery_cards[i]["text"]))
            
            if distance < min_distance:
                min_distance = distance
                selected_index = i
        
        # Debug output to console
        print(f"Final angle: {final_angle:.2f}°")
        print("Segment positions:")
        for i, center, dist, text in segment_positions:
            print(f"  Segment {i}: {text} - Center: {center:.2f}°, Distance: {dist:.2f}°")
        print(f"Selected: Segment {selected_index} - {self.mystery_cards[selected_index]['text']}")
        
        # Get the selected mystery card
        self.mystery_card = self.mystery_cards[selected_index]
        self.selected_mystery = self.mystery_card
        
        # Track this result to avoid repetition
        self.recent_mystery_results.append(selected_index)
        if len(self.recent_mystery_results) > self.max_recent_results:
            self.recent_mystery_results.pop(0)  # Remove oldest result
        
        # Add to used mysteries for randomization
        if self.mystery_card not in self.used_mysteries:
            self.used_mysteries.append(self.mystery_card)
        
        # Reset used mysteries if all have been used
        if len(self.used_mysteries) >= len(self.mystery_cards):
            self.used_mysteries = []

    def _draw_spin_wheel(self, center_x, center_y, radius):
        """Draw the spinning wheel"""
        # Draw wheel background
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (128, 0, 128), (center_x, center_y), radius, 8)
        pygame.draw.circle(self.screen, (255, 215, 0), (center_x, center_y), radius, 3)
        
        # Draw wheel segments
        num_cards = len(self.mystery_cards)
        angle_per_segment = 360 / num_cards
        
        for i, card in enumerate(self.mystery_cards):
            # Calculate segment angles - first segment starts at 0 degrees (top)
            # Convert to radians and adjust for rotation
            start_angle_deg = (i * angle_per_segment + self.spin_angle) % 360
            end_angle_deg = ((i + 1) * angle_per_segment + self.spin_angle) % 360
            
            # Convert to radians
            start_angle = math.radians(start_angle_deg)
            end_angle = math.radians(end_angle_deg)
            
            # Create points for the circular sector
            points = [(center_x, center_y)]  # Center point
            
            # Add points along the arc - handle wraparound properly
            num_arc_points = 30  # More points for smoother arc
            
            # Check if segment crosses the 0-degree boundary
            if end_angle_deg < start_angle_deg:
                # Segment crosses 0 degrees - draw in two parts
                # First part: from start_angle to 2π (0 degrees)
                for j in range(num_arc_points + 1):
                    t = j / num_arc_points
                    angle = start_angle + t * (2 * math.pi - start_angle)
                    x = center_x + radius * 0.9 * math.cos(angle)
                    y = center_y + radius * 0.9 * math.sin(angle)
                    points.append((x, y))
                
                # Second part: from 0 to end_angle
                for j in range(num_arc_points + 1):
                    t = j / num_arc_points
                    angle = t * end_angle
                    x = center_x + radius * 0.9 * math.cos(angle)
                    y = center_y + radius * 0.9 * math.sin(angle)
                    points.append((x, y))
            else:
                # Normal segment - no wraparound
                for j in range(num_arc_points + 1):
                    t = j / num_arc_points
                    angle = start_angle + t * (end_angle - start_angle)
                    x = center_x + radius * 0.9 * math.cos(angle)
                    y = center_y + radius * 0.9 * math.sin(angle)
                    points.append((x, y))
            
            # Fill segment with card color
            pygame.draw.polygon(self.screen, card["color"], points)
            pygame.draw.polygon(self.screen, (0, 0, 0), points, 2)
            
            # Draw segment text
            mid_angle_deg = (start_angle_deg + end_angle_deg) / 2
            # Handle wraparound for text positioning
            if end_angle_deg < start_angle_deg:
                mid_angle_deg = (start_angle_deg + end_angle_deg + 360) / 2
                if mid_angle_deg >= 360:
                    mid_angle_deg -= 360
            
            mid_angle = math.radians(mid_angle_deg)
            text_x = center_x + radius * 0.6 * math.cos(mid_angle)
            text_y = center_y + radius * 0.6 * math.sin(mid_angle)
            
            # Full text for each segment with better positioning
            text_surface = self.font.render(card["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(text_x, text_y))
            self.screen.blit(text_surface, text_rect)
        
        # Draw center circle
        pygame.draw.circle(self.screen, (183, 28, 28), (center_x, center_y), 30)
        pygame.draw.circle(self.screen, (255, 215, 0), (center_x, center_y), 30, 3)
        
        # Draw enhanced arrow pointer (positioned above wheel, pointing downward)
        arrow_length = 25
        arrow_width = 15
        arrow_tip_y = center_y - radius - 10
        
        # Main arrow body
        arrow_points = [
            (center_x, arrow_tip_y),  # Tip
            (center_x - arrow_width//2, arrow_tip_y + arrow_length),  # Bottom left
            (center_x - arrow_width//4, arrow_tip_y + arrow_length - 5),  # Inner left
            (center_x + arrow_width//4, arrow_tip_y + arrow_length - 5),  # Inner right
            (center_x + arrow_width//2, arrow_tip_y + arrow_length),  # Bottom right
        ]
        
        # Draw arrow shadow
        shadow_points = [(x + 2, y + 2) for x, y in arrow_points]
        pygame.draw.polygon(self.screen, (0, 0, 0, 100), shadow_points)
        
        # Draw main arrow
        pygame.draw.polygon(self.screen, (183, 28, 28), arrow_points)
        pygame.draw.polygon(self.screen, (255, 215, 0), arrow_points, 3)
        
        # Draw arrow shaft/line extending to wheel edge
        shaft_start_y = arrow_tip_y + arrow_length
        shaft_end_y = center_y - radius + 5
        pygame.draw.line(self.screen, (183, 28, 28), (center_x, shaft_start_y), (center_x, shaft_end_y), 4)
        pygame.draw.line(self.screen, (255, 215, 0), (center_x, shaft_start_y), (center_x, shaft_end_y), 2)
        
        # Draw selection indicator line on the wheel edge
        indicator_angle = 0  # Points to 0 degrees (top)
        indicator_x = center_x + radius * 0.95 * math.cos(math.radians(indicator_angle))
        indicator_y = center_y + radius * 0.95 * math.sin(math.radians(indicator_angle))
        
        # Draw small circle at selection point
        pygame.draw.circle(self.screen, (255, 255, 255), (int(indicator_x), int(indicator_y)), 8)
        pygame.draw.circle(self.screen, (183, 28, 28), (int(indicator_x), int(indicator_y)), 8, 3)
        pygame.draw.circle(self.screen, (255, 215, 0), (int(indicator_x), int(indicator_y)), 8, 1)

    def _show_sell_property(self):
        """Show property selling interface"""
        team = self.teams[self.current_idx]
        owned_properties = self._get_owned_properties(team.team_id)
        
        if not owned_properties:
            self.sell_property_feedback = "No properties to sell!"
            self.feedback_timer = 120
            return
            
        self.show_sell_property = True
        self.sell_property_feedback = None

    def _get_owned_properties(self, team_id):
        """Get list of properties owned by a team"""
        owned = []
        for i, prop in enumerate(self.properties):
            if prop["owner"] == team_id and i in self.property_data:
                prop_info = self.property_data[i]
                owned.append({
                    "index": i,
                    "name": prop_info["name"],
                    "price": prop_info["price"],
                    "color": prop_info["color"]
                })
        return owned

    def _sell_property(self, property_index):
        """Sell a property and give money to the team"""
        # Save state before selling
        self._save_state()
        
        team = self.teams[self.current_idx]
        prop_info = self.property_data[property_index]
        
        # Calculate sell price as half the original price, then round to nearest 500k
        half_price = prop_info["price"] // 2
        sell_price = round(half_price / 500_000) * 500_000  # Round to nearest 500k
        
        # Give money to team
        team.balance += sell_price
        
        # Remove ownership
        self.properties[property_index]["owner"] = None
        
        # Show feedback
        self.sell_property_feedback = f"Sold {prop_info['name']} for ₹{sell_price/1_000_000:.1f}M"
        self.feedback_timer = 120
        
        # Close selling interface
        self.show_sell_property = False

    def _start_trading(self):
        """Start the property trading system"""
        self.show_trading = True
        self.trading_phase = 'select_property'
        self.trading_seller = self.current_idx
        self.trading_offers = {}
        self.trading_feedback = None
        self.trading_offer_amounts = {}  # Initialize offer amounts for each team

    def _select_property_for_trade(self, property_index):
        """Select a property to trade"""
        team = self.teams[self.current_idx]
        if self.properties[property_index]["owner"] == team.team_id:
            self.trading_property = property_index
            self.trading_phase = 'collect_offers'
            self.trading_feedback = f"Property selected! Other players can now make offers."
        else:
            self.trading_feedback = "You don't own this property!"

    def _adjust_trading_offer(self, buyer_team_idx, delta):
        """Adjust trading offer amount for a team"""
        if self.trading_phase != 'collect_offers':
            return
        
        buyer_team = self.teams[buyer_team_idx]
        team_id = buyer_team.team_id
        
        # Initialize offer amount if not set
        if team_id not in self.trading_offer_amounts:
            self.trading_offer_amounts[team_id] = 500_000  # Start with 0.5M
        
        # Adjust amount
        new_amount = self.trading_offer_amounts[team_id] + delta
        
        # Ensure amount is within valid range
        if new_amount < 500_000:  # Minimum 0.5M
            new_amount = 500_000
        elif new_amount > buyer_team.balance:  # Can't exceed team's balance
            new_amount = buyer_team.balance
        
        self.trading_offer_amounts[team_id] = new_amount
        
        # Update the actual offer
        self.trading_offers[team_id] = new_amount
        self.trading_feedback = f"{buyer_team.name} offer: ₹{new_amount/1_000_000:.1f}M"

    def _make_trading_offer(self, buyer_team_idx, offer_amount):
        """Make an offer for the trading property"""
        if self.trading_phase != 'collect_offers':
            return
        
        buyer_team = self.teams[buyer_team_idx]
        if buyer_team.balance >= offer_amount:
            self.trading_offers[buyer_team.team_id] = offer_amount
            self.trading_feedback = f"{buyer_team.name} offered ₹{offer_amount/1_000_000:.1f}M"
        else:
            self.trading_feedback = f"{buyer_team.name} doesn't have enough money!"

    def _choose_trading_buyer(self, buyer_team_id):
        """Choose which buyer to sell the property to"""
        if buyer_team_id not in self.trading_offers:
            return
        
        # Save state before trading
        self._save_state()
        
        offer_amount = self.trading_offers[buyer_team_id]
        seller_team = self.teams[self.trading_seller]
        buyer_team = next(t for t in self.teams if t.team_id == buyer_team_id)
        
        # Transfer money
        buyer_team.balance -= offer_amount
        seller_team.balance += offer_amount
        
        # Transfer property
        self.properties[self.trading_property]["owner"] = buyer_team_id
        
        # Show feedback
        prop_info = self.property_data[self.trading_property]
        self.trading_feedback = f"Sold {prop_info['name']} to {buyer_team.name} for ₹{offer_amount/1_000_000:.1f}M"
        
        # Close trading
        self.show_trading = False
        self.trading_phase = None
        self.trading_offers = {}

    def _cancel_trading(self):
        """Cancel the trading process"""
        self.show_trading = False
        self.trading_phase = None
        self.trading_offers = {}
        self.trading_feedback = None
        self.trading_offer_amounts = {}

    def _draw_sell_property_overlay(self):
        if not self.show_sell_property:
            return
            
        team = self.teams[self.current_idx]
        owned_properties = self._get_owned_properties(team.team_id)
        
        if not owned_properties:
            return
            
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        self.screen.blit(overlay, (0,0))
        
        br = self.board_rect
        box_w = max(500, int(br.width * 0.8))
        box_h = min(400, len(owned_properties) * 60 + 120)
        box = pygame.Rect(0, 0, min(box_w, br.width - 20), min(box_h, br.height - 20))
        box.center = br.center
        
        # Enhanced box with shadow and borders
        shadow_rect = box.copy()
        shadow_rect.x += 8
        shadow_rect.y += 8
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect(), border_radius=16)
        self.screen.blit(shadow_surface, shadow_rect)
        
        pygame.draw.rect(self.screen, (255,255,255), box, border_radius=14)
        pygame.draw.rect(self.screen, (183, 28, 28), box, 4, border_radius=14)
        pygame.draw.rect(self.screen, (255, 215, 0), box, 2, border_radius=14)
        
        # Title
        title_bg = pygame.Rect(box.x + 10, box.y + 10, box.width - 20, 40)
        pygame.draw.rect(self.screen, (183, 28, 28), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), title_bg, 2, border_radius=8)
        
        title = self.big_font.render(f"* SELL PROPERTY - {team.name}", True, (255,255,255))
        self.screen.blit(title, (box.x+20, box.y+16))
        
        # Properties list
        y_offset = box.y + 60
        for prop in owned_properties:
            prop_rect = pygame.Rect(box.x + 20, y_offset, box.width - 40, 50)
            
            # Property background
            pygame.draw.rect(self.screen, (247,249,252), prop_rect, border_radius=8)
            pygame.draw.rect(self.screen, prop["color"], prop_rect, 3, border_radius=8)
            
            # Property name
            name_text = self.font.render(prop["name"], True, (20,20,20))
            self.screen.blit(name_text, (prop_rect.x + 10, prop_rect.y + 8))
            
            # Sell price (half of original price, rounded to nearest 500k)
            half_price = prop["price"] // 2
            sell_price = round(half_price / 500_000) * 500_000  # Round to nearest 500k
            price_text = self.font.render(f"Sell for: ₹{sell_price/1_000_000:.1f}M", True, (20,20,20))
            self.screen.blit(price_text, (prop_rect.x + 10, prop_rect.y + 28))
            
            # Sell button
            sell_btn = pygame.Rect(prop_rect.right - 80, prop_rect.y + 10, 70, 30)
            pygame.draw.rect(self.screen, (183,28,28), sell_btn, border_radius=6)
            pygame.draw.rect(self.screen, (255,255,255), sell_btn, 2, border_radius=6)
            
            sell_text = self.font.render("SELL", True, (255,255,255))
            self._blit_center_surface(sell_text, sell_btn)
            
            # Register clickable area
            def sell_action(idx=prop["index"]):
                return lambda: self._sell_property(idx)
            self.click_areas.append((sell_btn, sell_action()))
            
            y_offset += 60
        
        # Close button
        close_btn = pygame.Rect(box.centerx - 50, box.bottom - 50, 100, 35)
        pygame.draw.rect(self.screen, (100,100,100), close_btn, border_radius=8)
        close_text = self.font.render("CLOSE", True, (255,255,255))
        self._blit_center_surface(close_text, close_btn)
        self.click_areas.append((close_btn, lambda: setattr(self, 'show_sell_property', False)))

    def _draw_trading_overlay(self):
        if not self.show_trading:
            return
            
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        self.screen.blit(overlay, (0,0))
        
        br = self.board_rect
        box_w = max(600, int(br.width * 0.9))
        box_h = min(500, self.screen_h - 100)
        box = pygame.Rect(0, 0, min(box_w, br.width - 20), min(box_h, br.height - 20))
        box.center = br.center
        
        # Enhanced box with shadow and borders
        shadow_rect = box.copy()
        shadow_rect.x += 8
        shadow_rect.y += 8
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect(), border_radius=16)
        self.screen.blit(shadow_surface, shadow_rect)
        
        pygame.draw.rect(self.screen, (255,255,255), box, border_radius=14)
        pygame.draw.rect(self.screen, (183, 28, 28), box, 4, border_radius=14)
        pygame.draw.rect(self.screen, (255, 215, 0), box, 2, border_radius=14)
        
        # Title
        title_bg = pygame.Rect(box.x + 10, box.y + 10, box.width - 20, 40)
        pygame.draw.rect(self.screen, (183, 28, 28), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), title_bg, 2, border_radius=8)
        
        title = self.big_font.render(f"🤝 PROPERTY TRADING - {self.teams[self.trading_seller].name}", True, (255,255,255))
        self.screen.blit(title, (box.x+20, box.y+16))
        
        if self.trading_phase == 'select_property':
            # Show owned properties for selection
            owned_properties = self._get_owned_properties(self.teams[self.trading_seller].team_id)
            if not owned_properties:
                no_props_text = self.font.render("No properties to trade!", True, (100, 100, 100))
                self.screen.blit(no_props_text, (box.x + 20, box.y + 60))
            else:
                y_offset = box.y + 60
                for prop in owned_properties:
                    prop_rect = pygame.Rect(box.x + 20, y_offset, box.width - 40, 50)
                    
                    # Property background
                    pygame.draw.rect(self.screen, (247,249,252), prop_rect, border_radius=8)
                    pygame.draw.rect(self.screen, prop["color"], prop_rect, 3, border_radius=8)
                    
                    # Property name
                    name_text = self.font.render(prop["name"], True, (20,20,20))
                    self.screen.blit(name_text, (prop_rect.x + 10, prop_rect.y + 8))
                    
                    # Price
                    price_text = self.font.render(f"Price: ₹{prop['price']/1_000_000:.1f}M", True, (20,20,20))
                    self.screen.blit(price_text, (prop_rect.x + 10, prop_rect.y + 28))
                    
                    # Select button
                    select_btn = pygame.Rect(prop_rect.right - 100, prop_rect.y + 10, 90, 30)
                    pygame.draw.rect(self.screen, (34,139,34), select_btn, border_radius=6)
                    pygame.draw.rect(self.screen, (255,255,255), select_btn, 2, border_radius=6)
                    
                    select_text = self.font.render("SELECT", True, (255,255,255))
                    self._blit_center_surface(select_text, select_btn)
                    
                    # Register clickable area
                    def select_action(idx=prop["index"]):
                        return lambda: self._select_property_for_trade(idx)
                    self.click_areas.append((select_btn, select_action()))
                    
                    y_offset += 60
        
        elif self.trading_phase == 'collect_offers':
            # Show property being traded
            if self.trading_property is not None:
                prop_info = self.property_data[self.trading_property]
                prop_text = self.font.render(f"Trading: {prop_info['name']}", True, (20,20,20))
                self.screen.blit(prop_text, (box.x + 20, box.y + 60))
                
                # Show offer input for other players (no duplicate offer display)
                y_offset = box.y + 90
                for i, team in enumerate(self.teams):
                    if i != self.trading_seller:  # Not the seller
                        team_rect = pygame.Rect(box.x + 20, y_offset, box.width - 40, 50)
                        pygame.draw.rect(self.screen, (240,240,240), team_rect, border_radius=6)
                        pygame.draw.rect(self.screen, team.color, team_rect, 2, border_radius=6)
                        
                        # Team name
                        name_text = self.font.render(f"{team.name} (Balance: ₹{team.balance/1_000_000:.1f}M)", True, (20,20,20))
                        self.screen.blit(name_text, (team_rect.x + 10, team_rect.y + 8))
                        
                        # Current offer amount
                        current_offer = self.trading_offer_amounts.get(team.team_id, 500_000)
                        offer_text = self.font.render(f"Offer: ₹{current_offer/1_000_000:.1f}M", True, (20,20,20))
                        self.screen.blit(offer_text, (team_rect.x + 10, team_rect.y + 25))
                        
                        # Offer adjustment buttons
                        minus_btn = pygame.Rect(team_rect.right - 120, team_rect.y + 15, 30, 20)
                        plus_btn = pygame.Rect(team_rect.right - 80, team_rect.y + 15, 30, 20)
                        
                        # Minus button
                        pygame.draw.rect(self.screen, (244, 67, 54), minus_btn, border_radius=4)
                        minus_text = self.font.render("-0.5M", True, (255,255,255))
                        self._blit_center_surface(minus_text, minus_btn)
                        
                        # Plus button
                        pygame.draw.rect(self.screen, (34,139,34), plus_btn, border_radius=4)
                        plus_text = self.font.render("+0.5M", True, (255,255,255))
                        self._blit_center_surface(plus_text, plus_btn)
                        
                        # Register clickable areas
                        def adjust_minus(team_idx=i):
                            return lambda: self._adjust_trading_offer(team_idx, -500_000)
                        def adjust_plus(team_idx=i):
                            return lambda: self._adjust_trading_offer(team_idx, 500_000)
                        
                        self.click_areas.append((minus_btn, adjust_minus()))
                        self.click_areas.append((plus_btn, adjust_plus()))
                        
                        y_offset += 60
                
                # Add Review Offers button with status indicator
                review_btn = pygame.Rect(box.centerx - 80, y_offset + 20, 160, 35)
                
                # Show status of offers
                if self.trading_offers:
                    status_text = self.font.render(f"{len(self.trading_offers)} offer(s) ready", True, (34,139,34))
                    self.screen.blit(status_text, (box.centerx - status_text.get_width()//2, y_offset + 5))
                    # Green button when offers are ready
                    pygame.draw.rect(self.screen, (34,139,34), review_btn, border_radius=8)
                else:
                    status_text = self.font.render("No offers yet", True, (100,100,100))
                    self.screen.blit(status_text, (box.centerx - status_text.get_width()//2, y_offset + 5))
                    # Gray button when no offers
                    pygame.draw.rect(self.screen, (100,100,100), review_btn, border_radius=8)
                
                pygame.draw.rect(self.screen, (255,255,255), review_btn, 2, border_radius=8)
                review_text = self.font.render("REVIEW OFFERS", True, (255,255,255))
                self._blit_center_surface(review_text, review_btn)
                self.click_areas.append((review_btn, lambda: setattr(self, 'trading_phase', 'choose_buyer')))
        
        elif self.trading_phase == 'choose_buyer':
            # Show offers and let seller choose
            if self.trading_offers:
                choose_text = self.font.render("Choose a buyer:", True, (20,20,20))
                self.screen.blit(choose_text, (box.x + 20, box.y + 60))
                
                # Back to offers button
                back_btn = pygame.Rect(box.x + 20, box.y + 85, 120, 30)
                pygame.draw.rect(self.screen, (100,100,100), back_btn, border_radius=6)
                pygame.draw.rect(self.screen, (255,255,255), back_btn, 2, border_radius=6)
                back_text = self.font.render("BACK TO OFFERS", True, (255,255,255))
                self._blit_center_surface(back_text, back_btn)
                self.click_areas.append((back_btn, lambda: setattr(self, 'trading_phase', 'collect_offers')))
                
                y_offset = box.y + 130
                for team_id, offer in self.trading_offers.items():
                    team = next(t for t in self.teams if t.team_id == team_id)
                    
                    buyer_rect = pygame.Rect(box.x + 20, y_offset, box.width - 40, 50)
                    pygame.draw.rect(self.screen, (247,249,252), buyer_rect, border_radius=8)
                    pygame.draw.rect(self.screen, team.color, buyer_rect, 3, border_radius=8)
                    
                    # Team name and offer
                    offer_text = self.font.render(f"{team.name} - ₹{offer/1_000_000:.1f}M", True, (20,20,20))
                    self.screen.blit(offer_text, (buyer_rect.x + 10, buyer_rect.y + 15))
                    
                    # Accept button
                    accept_btn = pygame.Rect(buyer_rect.right - 80, buyer_rect.y + 10, 70, 30)
                    pygame.draw.rect(self.screen, (34,139,34), accept_btn, border_radius=6)
                    pygame.draw.rect(self.screen, (255,255,255), accept_btn, 2, border_radius=6)
                    
                    accept_text = self.font.render("ACCEPT", True, (255,255,255))
                    self._blit_center_surface(accept_text, accept_btn)
                    
                    # Register clickable area
                    def accept_offer(team_id=team_id):
                        return lambda: self._choose_trading_buyer(team_id)
                    self.click_areas.append((accept_btn, accept_offer()))
                    
                    y_offset += 60
        
        # Cancel button
        cancel_btn = pygame.Rect(box.centerx - 50, box.bottom - 50, 100, 35)
        pygame.draw.rect(self.screen, (100,100,100), cancel_btn, border_radius=8)
        cancel_text = self.font.render("CANCEL", True, (255,255,255))
        self._blit_center_surface(cancel_text, cancel_btn)
        self.click_areas.append((cancel_btn, self._cancel_trading))
        
        # Show feedback
        if self.trading_feedback:
            feedback_text = self.font.render(self.trading_feedback, True, (20,20,20))
            self.screen.blit(feedback_text, (box.x + 20, box.bottom - 80))

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                lines.append(self.font.render(cur, True, (20,20,20)))
                cur = w
        if cur:
            lines.append(self.font.render(cur, True, (20,20,20)))
        return lines

    def _ease_in_out(self, t):
        # smoothstep-like easing
        return t * t * (3 - 2 * t)

    def _blit_center(self, text, pos, font, color):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(int(pos[0]), int(pos[1])))
        self.screen.blit(surf, rect)

    def _blit_center_surface(self, surf, rect):
        r = surf.get_rect(center=rect.center)
        self.screen.blit(surf, r)

    def _draw_button_icon(self, label, rect):
        """Draw a simple icon for each button based on its label"""
        icon_size = 16
        icon_x = rect.x + 15
        icon_y = rect.centery - icon_size // 2
        
        if "Roll Dice" in label:
            # Draw dice icon (square with dots)
            pygame.draw.rect(self.screen, (255, 255, 255), (icon_x, icon_y, icon_size, icon_size), 2)
            # Draw center dot
            pygame.draw.circle(self.screen, (255, 255, 255), (icon_x + icon_size//2, icon_y + icon_size//2), 2)
        elif "Buy" in label:
            # Draw house icon (triangle on rectangle)
            house_x, house_y = icon_x, icon_y
            # House base
            pygame.draw.rect(self.screen, (255, 255, 255), (house_x + 2, house_y + 6, icon_size - 4, icon_size - 6), 2)
            # House roof (triangle)
            points = [(house_x, house_y + 6), (house_x + icon_size//2, house_y), (house_x + icon_size, house_y + 6)]
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)
        elif "End Turn" in label:
            # Draw arrow icon
            arrow_x, arrow_y = icon_x, icon_y
            pygame.draw.line(self.screen, (255, 255, 255), (arrow_x, arrow_y + icon_size//2), (arrow_x + icon_size, arrow_y + icon_size//2), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (arrow_x + icon_size - 4, arrow_y + 4), (arrow_x + icon_size, arrow_y + icon_size//2), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (arrow_x + icon_size - 4, arrow_y + icon_size - 4), (arrow_x + icon_size, arrow_y + icon_size//2), 2)
        elif "Test Chance" in label:
            # Draw star icon
            star_x, star_y = icon_x, icon_y
            center_x, center_y = star_x + icon_size//2, star_y + icon_size//2
            # Draw a simple star shape
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 6, 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 2)
        elif "Test Mystery" in label:
            # Draw question mark icon
            q_x, q_y = icon_x, icon_y
            pygame.draw.circle(self.screen, (255, 255, 255), (q_x + icon_size//2, q_y + icon_size//2), 6, 2)
            # Draw question mark
            pygame.draw.line(self.screen, (255, 255, 255), (q_x + icon_size//2, q_y + 4), (q_x + icon_size//2, q_y + 8), 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (q_x + icon_size//2, q_y + 10), 1)
        elif "Undo" in label:
            # Draw undo arrow icon (curved arrow pointing left)
            undo_x, undo_y = icon_x, icon_y
            center_x, center_y = undo_x + icon_size//2, undo_y + icon_size//2
            # Draw curved arrow pointing left
            pygame.draw.arc(self.screen, (255, 255, 255), (undo_x + 2, undo_y + 2, icon_size - 4, icon_size - 4), 0, 3.14, 2)
            # Draw arrow head
            pygame.draw.line(self.screen, (255, 255, 255), (undo_x + 4, undo_y + 4), (undo_x + 8, undo_y + 4), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (undo_x + 4, undo_y + 4), (undo_x + 6, undo_y + 2), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (undo_x + 4, undo_y + 4), (undo_x + 6, undo_y + 6), 2)
        elif "Reset Game" in label:
            # Draw circular arrow icon
            reset_x, reset_y = icon_x, icon_y
            center_x, center_y = reset_x + icon_size//2, reset_y + icon_size//2
            # Draw circle
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 6, 2)
            # Draw arrow inside
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - 2, center_y + 2), (center_x + 2, center_y - 2), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (center_x + 2, center_y - 2), (center_x + 4, center_y), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (center_x + 2, center_y - 2), (center_x, center_y), 2)

    def _draw(self):
        self._draw_board()
        self._draw_houses()
        self._draw_tokens()
        self._draw_ui()
        self._draw_property_card()
        self._draw_chance_overlay()
        self._draw_chance_confirm_overlay()
        self._draw_mystery_overlay()
        self._draw_sell_property_overlay()
        self._draw_trading_overlay()
        
        # Feedback popup for chance result, mystery apply, property sell (trading feedback shown in overlay)
        if (self.chance_feedback and self.feedback_timer > 0) or self.mystery_feedback or self.sell_property_feedback:
            self._draw_feedback_popup()
        
        pygame.display.flip()

    def _draw_feedback_popup(self):
        msg = (self.chance_feedback if (self.chance_feedback and self.feedback_timer > 0) 
               else self.mystery_feedback if self.mystery_feedback 
               else self.sell_property_feedback)
        if not msg:
            return
        text = self.big_font.render(msg, True, (255,255,255))
        bg_rect = text.get_rect()
        bg_rect.inflate_ip(40, 20)
        bg_rect.center = self.board_rect.center
        
        # Enhanced background with shadow and borders
        shadow_rect = bg_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 60), shadow_surface.get_rect(), border_radius=14)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Background with color and enhanced borders
        color = (76,175,80) if "Correct" in msg or "Gained" in msg or "Moved" in msg or "Sold" in msg else (244,67,54)
        pygame.draw.rect(self.screen, (0,0,0,180), bg_rect.inflate(4,4), border_radius=12)
        pygame.draw.rect(self.screen, color, bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, 1, border_radius=12)
        
        self.screen.blit(text, bg_rect)


if __name__ == "__main__":
    Game().run()


