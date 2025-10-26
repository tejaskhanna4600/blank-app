#!/usr/bin/env python3
"""
Arthvidya Monopoly - Multi-Client Startup Script
This script starts both the pygame game and the Streamlit web interface
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

class GameManager:
    def __init__(self):
        self.game_process = None
        self.streamlit_process = None
        self.running = False
        
    def start_game(self):
        """Start the pygame game"""
        try:
            print("🎮 Starting Pygame Monopoly Game...")
            self.game_process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Pygame game started successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to start pygame game: {e}")
            return False
    
    def start_streamlit(self):
        """Start the Streamlit web interface"""
        try:
            print("🌐 Starting Streamlit Web Interface...")
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "streamlit_client.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0",
                "--server.headless", "true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Streamlit interface started successfully!")
            print("🌐 Web interface available at: http://localhost:8501")
            return True
        except Exception as e:
            print(f"❌ Failed to start Streamlit: {e}")
            return False
    
    def stop_all(self):
        """Stop both processes"""
        print("\n🛑 Shutting down...")
        self.running = False
        
        if self.game_process:
            print("🛑 Stopping pygame game...")
            self.game_process.terminate()
            self.game_process.wait()
            print("✅ Pygame game stopped")
        
        if self.streamlit_process:
            print("🛑 Stopping Streamlit interface...")
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
            print("✅ Streamlit interface stopped")
    
    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        while self.running:
            try:
                # Check game process
                if self.game_process and self.game_process.poll() is not None:
                    print("⚠️ Pygame game process ended unexpectedly")
                    if self.running:
                        print("🔄 Restarting pygame game...")
                        self.start_game()
                
                # Check Streamlit process
                if self.streamlit_process and self.streamlit_process.poll() is not None:
                    print("⚠️ Streamlit process ended unexpectedly")
                    if self.running:
                        print("🔄 Restarting Streamlit interface...")
                        self.start_streamlit()
                
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error monitoring processes: {e}")
                time.sleep(5)
    
    def run(self):
        """Main run method"""
        print("🎲 Arthvidya Monopoly - Multi-Client System")
        print("=" * 50)
        
        # Check if required files exist
        required_files = ["main.py", "streamlit_client.py"]
        for file in required_files:
            if not Path(file).exists():
                print(f"❌ Required file not found: {file}")
                return False
        
        # Start both processes
        game_started = self.start_game()
        streamlit_started = self.start_streamlit()
        
        if not game_started or not streamlit_started:
            print("❌ Failed to start one or more processes")
            self.stop_all()
            return False
        
        self.running = True
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            print(f"\n📡 Received signal {signum}")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("\n🎮 Both systems are running!")
        print("📋 Instructions:")
        print("   • Control Center: http://localhost:8501")
        print("   • Team Interfaces: http://localhost:8501 (select team from sidebar)")
        print("   • Press Ctrl+C to stop all processes")
        print("=" * 50)
        
        try:
            # Monitor processes
            self.monitor_processes()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
        
        return True

def main():
    """Main function"""
    manager = GameManager()
    success = manager.run()
    
    if success:
        print("✅ System shutdown complete")
    else:
        print("❌ System startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
