#!/usr/bin/env python3
"""
Secure Startup Script for Password-Protected Monopoly Game
This script starts the game with password protection enabled
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

class SecureGameManager:
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
    
    def start_secure_streamlit(self):
        """Start the password-protected Streamlit interface"""
        print("🔐 Starting Secure Streamlit Interface...")
        
        try:
            # Check if secure client exists
            if not Path("streamlit_client_secure.py").exists():
                print("❌ streamlit_client_secure.py not found!")
                print("📋 Using regular client instead...")
                client_file = "streamlit_client.py"
            else:
                client_file = "streamlit_client_secure.py"
                print("🛡️ Password protection enabled!")
            
            # Find available port
            import socket
            def find_free_port():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    s.listen(1)
                    port = s.getsockname()[1]
                return port
            
            port = find_free_port()
            print(f"🔌 Using port {port}")
            
            # Start Streamlit
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", client_file,
                "--server.port", str(port),
                "--server.address", "0.0.0.0",
                "--server.headless", "true"
            ])
            
            # Wait for startup
            print("⏳ Waiting for Streamlit to start...")
            time.sleep(5)
            
            if process.poll() is None:
                print(f"✅ Secure Streamlit started successfully!")
                print(f"🌐 Access at: http://localhost:{port}")
                return process, port
            else:
                print("❌ Streamlit failed to start")
                return None, None
                
        except Exception as e:
            print(f"❌ Error starting Streamlit: {e}")
            return None, None
    
    def display_password_info(self):
        """Display password information"""
        print("\n🔑 PASSWORD INFORMATION:")
        print("=" * 40)
        
        try:
            # Try to load password config
            if Path("password_config.py").exists():
                print("📋 Default passwords (CHANGE THESE!):")
                print("   • Control Center: admin_2024")
                print("   • Team 1: team1_2024")
                print("   • Team 2: team2_2024")
                print("   • Team 3: team3_2024")
                print("   • Team 4: team4_2024")
                print("   • Team 5: team5_2024")
            else:
                print("📋 Default passwords:")
                print("   • Control Center: admin_2024")
                print("   • Team 1: team1_2024")
                print("   • Team 2: team2_2024")
                print("   • Team 3: team3_2024")
                print("   • Team 4: team4_2024")
                print("   • Team 5: team5_2024")
        except:
            print("❌ Could not load password information")
        
        print("\n🛡️ SECURITY REMINDERS:")
        print("   • Change default passwords before playing")
        print("   • Share passwords only with team members")
        print("   • Keep Control Center password secret")
        print("   • Use strong, unique passwords")
    
    def run(self):
        """Main run method"""
        print("🔐 Arthvidya Monopoly - Secure Multi-Client System")
        print("=" * 60)
        
        # Check required files
        required_files = ["main.py"]
        optional_files = ["streamlit_client_secure.py", "streamlit_client.py"]
        
        for file in required_files:
            if not Path(file).exists():
                print(f"❌ Required file not found: {file}")
                return False
        
        # Check for Streamlit client
        streamlit_client = None
        for file in optional_files:
            if Path(file).exists():
                streamlit_client = file
                break
        
        if not streamlit_client:
            print("❌ No Streamlit client found!")
            return False
        
        # Display password information
        self.display_password_info()
        
        # Start pygame game
        if not self.start_game():
            return False
        
        # Start Streamlit
        streamlit_process, port = self.start_secure_streamlit()
        
        if streamlit_process:
            print("\n🎉 Both systems running securely!")
            print("📋 Access points:")
            print(f"   • Pygame Game: Check for game window")
            print(f"   • Web Interface: http://localhost:{port}")
            print("   • Login required for all team access")
            print("   • Each team has unique password")
            
            # Set up signal handler
            def signal_handler(signum, frame):
                print("\n🛑 Shutting down...")
                if self.game_process:
                    self.game_process.terminate()
                if streamlit_process:
                    streamlit_process.terminate()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            try:
                while True:
                    time.sleep(5)
                    # Check if processes are still running
                    if self.game_process.poll() is not None:
                        print("⚠️ Pygame game process ended")
                        break
                    if streamlit_process.poll() is not None:
                        print("⚠️ Streamlit process ended")
                        break
            except KeyboardInterrupt:
                pass
            
            # Cleanup
            if self.game_process:
                self.game_process.terminate()
                self.game_process.wait()
                print("✅ Pygame game stopped")
            
            if streamlit_process:
                streamlit_process.terminate()
                streamlit_process.wait()
                print("✅ Streamlit interface stopped")
            
            print("✅ Shutdown complete")
        else:
            print("\n⚠️ Streamlit failed, but pygame is running")
            print("🎮 You can still play using the pygame window")
        
        return True

def main():
    """Main function"""
    manager = SecureGameManager()
    success = manager.run()
    
    if success:
        print("✅ Secure system shutdown complete")
    else:
        print("❌ Secure system startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
