#!/usr/bin/env python3
"""
Streamlit Troubleshooting and Alternative Startup Script
This script helps diagnose and fix Streamlit issues
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

def check_streamlit_installation():
    """Check if Streamlit is properly installed"""
    print("🔍 Checking Streamlit installation...")
    
    try:
        result = subprocess.run([sys.executable, "-c", "import streamlit; print(streamlit.__version__)"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Streamlit is installed: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Streamlit import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking Streamlit: {e}")
        return False

def install_streamlit():
    """Install Streamlit if not present"""
    print("📦 Installing Streamlit...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
        print("✅ Streamlit installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Streamlit: {e}")
        return False

def test_streamlit_basic():
    """Test basic Streamlit functionality"""
    print("🧪 Testing basic Streamlit functionality...")
    
    # Create a simple test app
    test_app_content = '''
import streamlit as st
st.title("Test App")
st.write("If you can see this, Streamlit is working!")
'''
    
    test_file = "test_streamlit.py"
    try:
        with open(test_file, 'w') as f:
            f.write(test_app_content)
        
        # Try to run the test app
        print("🚀 Starting test Streamlit app...")
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", test_file,
            "--server.port", "8502",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for startup
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Streamlit test app started successfully!")
            process.terminate()
            process.wait()
            os.remove(test_file)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit test failed:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            os.remove(test_file)
            return False
            
    except Exception as e:
        print(f"❌ Error testing Streamlit: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def create_simple_startup():
    """Create a simple startup script that handles errors better"""
    print("🔧 Creating improved startup script...")
    
    startup_content = '''#!/usr/bin/env python3
"""
Improved Streamlit Startup Script
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

class ImprovedGameManager:
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
    
    def start_streamlit_alternative(self):
        """Start Streamlit with alternative methods"""
        print("🌐 Starting Streamlit Web Interface...")
        
        # Try different startup methods
        methods = [
            # Method 1: Standard startup
            [sys.executable, "-m", "streamlit", "run", "streamlit_client.py", 
             "--server.port", "8501", "--server.address", "0.0.0.0"],
            
            # Method 2: With headless mode
            [sys.executable, "-m", "streamlit", "run", "streamlit_client.py", 
             "--server.port", "8501", "--server.headless", "true"],
            
            # Method 3: With different port
            [sys.executable, "-m", "streamlit", "run", "streamlit_client.py", 
             "--server.port", "8502", "--server.headless", "true"],
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Trying method {i}...")
                self.streamlit_process = subprocess.Popen(
                    method, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                
                # Wait a bit to see if it starts
                time.sleep(3)
                
                if self.streamlit_process.poll() is None:
                    port = method[-2] if method[-2].isdigit() else "8501"
                    print(f"✅ Streamlit started successfully on port {port}!")
                    print(f"🌐 Web interface: http://localhost:{port}")
                    return True
                else:
                    stdout, stderr = self.streamlit_process.communicate()
                    print(f"❌ Method {i} failed:")
                    if stderr:
                        print(f"Error: {stderr.decode()}")
                    continue
                    
            except Exception as e:
                print(f"❌ Method {i} exception: {e}")
                continue
        
        print("❌ All Streamlit startup methods failed")
        return False
    
    def run(self):
        """Main run method"""
        print("🎲 Arthvidya Monopoly - Improved Startup")
        print("=" * 50)
        
        # Check required files
        required_files = ["main.py", "streamlit_client.py"]
        for file in required_files:
            if not Path(file).exists():
                print(f"❌ Required file not found: {file}")
                return False
        
        # Start pygame game
        if not self.start_game():
            return False
        
        # Start Streamlit
        if not self.start_streamlit_alternative():
            print("⚠️ Streamlit failed to start, but pygame game is running")
            print("🎮 You can still play the pygame game directly")
            return True
        
        self.running = True
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            print(f"\\n📡 Received signal {signum}")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("\\n🎮 Both systems are running!")
        print("📋 Instructions:")
        print("   • Control Center: http://localhost:8501 (or 8502)")
        print("   • Team Interfaces: Select team from sidebar")
        print("   • Press Ctrl+C to stop all processes")
        print("=" * 50)
        
        try:
            # Simple monitoring loop
            while self.running:
                time.sleep(5)
                # Check if processes are still running
                if self.game_process and self.game_process.poll() is not None:
                    print("⚠️ Pygame game process ended")
                    break
                if self.streamlit_process and self.streamlit_process.poll() is not None:
                    print("⚠️ Streamlit process ended")
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
        
        return True
    
    def stop_all(self):
        """Stop both processes"""
        print("\\n🛑 Shutting down...")
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

def main():
    """Main function"""
    manager = ImprovedGameManager()
    success = manager.run()
    
    if success:
        print("✅ System shutdown complete")
    else:
        print("❌ System startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    try:
        with open("start_game_improved.py", 'w') as f:
            f.write(startup_content)
        print("✅ Improved startup script created: start_game_improved.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create improved startup script: {e}")
        return False

def create_manual_startup_guide():
    """Create a manual startup guide"""
    print("📖 Creating manual startup guide...")
    
    guide_content = '''# Manual Startup Guide for Streamlit Issues

## If Streamlit keeps failing, try these manual steps:

### Method 1: Start Streamlit Separately
1. Open a terminal/command prompt
2. Navigate to your game directory
3. Run: `streamlit run streamlit_client.py --server.port 8501`
4. Open another terminal
5. Run: `python main.py`

### Method 2: Use Different Port
1. Run: `streamlit run streamlit_client.py --server.port 8502`
2. Access: http://localhost:8502

### Method 3: Check Streamlit Installation
1. Run: `pip install --upgrade streamlit`
2. Run: `pip install --upgrade pip`
3. Try starting again

### Method 4: Use Conda (if you have it)
1. Run: `conda install streamlit`
2. Try starting again

### Method 5: Virtual Environment
1. Create virtual environment: `python -m venv venv`
2. Activate it:
   - Windows: `venv\\Scripts\\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install: `pip install streamlit`
4. Try starting again

### Method 6: Direct Python Execution
1. Run: `python -m streamlit run streamlit_client.py`

## Troubleshooting Commands

Check if Streamlit is working:
```bash
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

Check what's running on port 8501:
```bash
netstat -an | findstr 8501
```

Kill any existing Streamlit processes:
```bash
taskkill /f /im python.exe
```

## Alternative: Use Only Pygame
If Streamlit continues to fail, you can still play the game using only the pygame interface:
1. Run: `python main.py`
2. Use keyboard controls:
   - R: Roll dice
   - B: Buy property
   - E: End turn
   - S: Sell property
   - T: Start trading
   - U: Undo move
'''
    
    try:
        with open("MANUAL_STARTUP_GUIDE.md", 'w') as f:
            f.write(guide_content)
        print("✅ Manual startup guide created: MANUAL_STARTUP_GUIDE.md")
        return True
    except Exception as e:
        print(f"❌ Failed to create manual guide: {e}")
        return False

def main():
    """Main troubleshooting function"""
    print("🔧 Streamlit Troubleshooting Tool")
    print("=" * 40)
    
    # Step 1: Check Streamlit installation
    if not check_streamlit_installation():
        print("\n📦 Streamlit not found. Installing...")
        if not install_streamlit():
            print("❌ Failed to install Streamlit")
            return False
    
    # Step 2: Test Streamlit functionality
    if not test_streamlit_basic():
        print("\n❌ Streamlit basic test failed")
        print("🔧 Creating alternative solutions...")
    
    # Step 3: Create improved startup script
    create_simple_startup()
    
    # Step 4: Create manual guide
    create_manual_startup_guide()
    
    print("\n✅ Troubleshooting complete!")
    print("\n📋 Next steps:")
    print("1. Try the improved startup script: python start_game_improved.py")
    print("2. If that fails, follow the manual guide: MANUAL_STARTUP_GUIDE.md")
    print("3. Or start components separately:")
    print("   - Terminal 1: python main.py")
    print("   - Terminal 2: streamlit run streamlit_client.py")
    
    return True

if __name__ == "__main__":
    main()
