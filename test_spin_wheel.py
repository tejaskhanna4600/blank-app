#!/usr/bin/env python3
"""
Test script to verify spin wheel functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import Game
import pygame

def test_spin_wheel():
    """Test the spin wheel functionality"""
    print("Testing spin wheel functionality...")
    
    # Initialize pygame
    pygame.init()
    
    # Create game instance
    game = Game()
    
    # Test mystery cards
    print(f"Number of mystery cards: {len(game.mystery_cards)}")
    for i, card in enumerate(game.mystery_cards):
        print(f"Card {i+1}: {card['text']} (Type: {card['type']}, Color: {card['color']})")
    
    # Test spin wheel initialization
    print("\nTesting spin wheel initialization...")
    game._start_spin_wheel()
    print(f"Spinning: {game.spinning}")
    print(f"Spin angle: {game.spin_angle}")
    print(f"Spin target angle: {game.spin_target_angle}")
    print(f"Selected mystery: {game.selected_mystery}")
    
    # Test spin wheel update
    print("\nTesting spin wheel update...")
    for i in range(10):
        game._update_spin_wheel()
        print(f"Frame {i+1}: Angle={game.spin_angle:.1f}, Progress={game.spin_progress}, Spinning={game.spinning}")
        if not game.spinning:
            break
    
    # Test mystery application
    if game.selected_mystery:
        print(f"\nSelected mystery: {game.selected_mystery['text']}")
        print("Testing mystery application...")
        game._apply_mystery()
        print(f"Mystery feedback: {game.mystery_feedback}")
    
    print("\nSpin wheel test completed successfully!")
    pygame.quit()

if __name__ == "__main__":
    test_spin_wheel()


