#!/usr/bin/env python3
"""
Simple Alternative Startup Script
This script starts the game and Streamlit separately with better error handling
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def start_pygame_game():
    """Start the pygame game"""
    print("🎮 Starting Pygame Monopoly Game...")
    try:
        process = subprocess.Popen([sys.executable, "main.py"])
        print("✅ Pygame game started successfully!")
        print("🎮 Game window should open shortly...")
        return process
    except Exception as e:
        print(f"❌ Failed to start pygame game: {e}")
        return None

def start_streamlit():
    """Start Streamlit interface"""
    print("🌐 Starting Streamlit Web Interface...")
    
    # Try different methods to start Streamlit
    methods = [
        # Method 1: Standard
        [sys.executable, "-m", "streamlit", "run", "streamlit_client.py", "--server.port", "8501"],
        
        # Method 2: With headless
        [sys.executable, "-m", "streamlit", "run", "streamlit_client.py", "--server.port", "8501", "--server.headless", "true"],
        
        # Method 3: Different port
        [sys.executable, "-m", "streamlit", "run", "streamlit_client.py", "--server.port", "8502"],
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"🔄 Trying Streamlit method {i}...")
            process = subprocess.Popen(method, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait to see if it starts successfully
            time.sleep(3)
            
            if process.poll() is None:
                port = "8501" if "8501" in method else "8502"
                print(f"✅ Streamlit started successfully!")
                print(f"🌐 Web interface: http://localhost:{port}")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Method {i} failed")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                continue
                
        except Exception as e:
            print(f"❌ Method {i} exception: {e}")
            continue
    
    print("❌ All Streamlit methods failed")
    return None

def main():
    """Main function"""
    print("🎲 Arthvidya Monopoly - Simple Startup")
    print("=" * 50)
    
    # Check required files
    required_files = ["main.py", "streamlit_client.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file not found: {file}")
            return False
    
    # Start pygame game
    game_process = start_pygame_game()
    if not game_process:
        print("❌ Cannot start without pygame game")
        return False
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    
    if streamlit_process:
        print("\n🎉 Both systems started successfully!")
        print("📋 Access points:")
        print("   • Pygame Game: Check for game window")
        print("   • Web Interface: http://localhost:8501")
        print("   • Control Center: Select 'Control Center' from sidebar")
        print("   • Team Interfaces: Select team from sidebar")
    else:
        print("\n⚠️ Streamlit failed to start")
        print("🎮 Pygame game is still running")
        print("📋 You can:")
        print("   1. Play using the pygame window")
        print("   2. Try starting Streamlit manually:")
        print("      streamlit run streamlit_client.py")
        print("   3. Run the troubleshooting script:")
        print("      python troubleshoot_streamlit.py")
    
    print("\n🛑 Press Ctrl+C to stop all processes")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if game_process.poll() is not None:
                print("⚠️ Pygame game process ended")
                break
            if streamlit_process and streamlit_process.poll() is not None:
                print("⚠️ Streamlit process ended")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    # Clean up processes
    if game_process:
        game_process.terminate()
        game_process.wait()
        print("✅ Pygame game stopped")
    
    if streamlit_process:
        streamlit_process.terminate()
        streamlit_process.wait()
        print("✅ Streamlit interface stopped")
    
    print("✅ Shutdown complete")
    return True

if __name__ == "__main__":
    main()
