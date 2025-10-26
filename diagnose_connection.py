#!/usr/bin/env python3
"""
Connection Diagnostic Script
This script helps diagnose why localhost is refusing connections
"""

import subprocess
import sys
import time
import socket
import os
from pathlib import Path

def check_port_availability(port):
    """Check if a port is available"""
    print(f"🔍 Checking port {port} availability...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"❌ Port {port} is already in use")
            return False
        else:
            print(f"✅ Port {port} is available")
            return True
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
        return False

def check_streamlit_files():
    """Check if required Streamlit files exist"""
    print("📁 Checking required files...")
    
    required_files = ["streamlit_client.py", "main.py"]
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_streamlit_startup():
    """Test if Streamlit can start properly"""
    print("🧪 Testing Streamlit startup...")
    
    try:
        # Try to start Streamlit in test mode
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_client.py",
            "--server.port", "8503",  # Use different port for testing
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Streamlit started successfully!")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Streamlit failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Streamlit: {e}")
        return False

def check_python_environment():
    """Check Python environment"""
    print("🐍 Checking Python environment...")
    
    try:
        # Check Python version
        version = sys.version_info
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("⚠️ Python 3.8+ recommended")
        
        # Check if streamlit module can be imported
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
        
        return True
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking Python environment: {e}")
        return False

def create_working_startup_script():
    """Create a guaranteed working startup script"""
    print("🔧 Creating guaranteed working startup script...")
    
    script_content = '''#!/usr/bin/env python3
"""
Guaranteed Working Startup Script
This script ensures both components start properly
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def start_pygame():
    """Start pygame game"""
    print("🎮 Starting Pygame Game...")
    try:
        process = subprocess.Popen([sys.executable, "main.py"])
        print("✅ Pygame game started!")
        return process
    except Exception as e:
        print(f"❌ Failed to start pygame: {e}")
        return None

def start_streamlit_guaranteed():
    """Start Streamlit with guaranteed success"""
    print("🌐 Starting Streamlit...")
    
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
    
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_client.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
        
        # Wait for startup
        print("⏳ Waiting for Streamlit to start...")
        time.sleep(5)
        
        if process.poll() is None:
            print(f"✅ Streamlit started successfully!")
            print(f"🌐 Access at: http://localhost:{port}")
            return process, port
        else:
            print("❌ Streamlit failed to start")
            return None, None
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return None, None

def main():
    """Main function"""
    print("🎲 Arthvidya Monopoly - Guaranteed Startup")
    print("=" * 50)
    
    # Check files
    if not Path("streamlit_client.py").exists():
        print("❌ streamlit_client.py not found")
        return False
    
    if not Path("main.py").exists():
        print("❌ main.py not found")
        return False
    
    # Start pygame
    game_process = start_pygame()
    if not game_process:
        return False
    
    # Start Streamlit
    streamlit_process, port = start_streamlit_guaranteed()
    
    if streamlit_process:
        print("\\n🎉 Both systems running!")
        print(f"📋 Access points:")
        print(f"   • Pygame: Check for game window")
        print(f"   • Web Interface: http://localhost:{port}")
        print(f"   • Control Center: Select from sidebar")
        print(f"   • Team Interfaces: Select team from sidebar")
        
        # Set up signal handler
        def signal_handler(signum, frame):
            print("\\n🛑 Shutting down...")
            if game_process:
                game_process.terminate()
            if streamlit_process:
                streamlit_process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while True:
                time.sleep(1)
                if game_process.poll() is not None:
                    print("⚠️ Pygame ended")
                    break
                if streamlit_process.poll() is not None:
                    print("⚠️ Streamlit ended")
                    break
        except KeyboardInterrupt:
            pass
        
        # Cleanup
        if game_process:
            game_process.terminate()
        if streamlit_process:
            streamlit_process.terminate()
        
        print("✅ Shutdown complete")
    else:
        print("\\n⚠️ Streamlit failed, but pygame is running")
        print("🎮 You can still play using the pygame window")
    
    return True

if __name__ == "__main__":
    main()
'''
    
    try:
        with open("start_guaranteed.py", 'w') as f:
            f.write(script_content)
        print("✅ Created: start_guaranteed.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create script: {e}")
        return False

def provide_manual_solutions():
    """Provide manual solutions"""
    print("\\n📋 Manual Solutions:")
    print("=" * 30)
    
    print("\\n🔧 Solution 1: Start Components Separately")
    print("Open TWO separate terminals:")
    print("Terminal 1: python main.py")
    print("Terminal 2: streamlit run streamlit_client.py --server.port 8501")
    
    print("\\n🔧 Solution 2: Use Different Port")
    print("streamlit run streamlit_client.py --server.port 8502")
    print("Then access: http://localhost:8502")
    
    print("\\n🔧 Solution 3: Check What's Using Port 8501")
    print("Windows: netstat -an | findstr 8501")
    print("Mac/Linux: lsof -i :8501")
    
    print("\\n🔧 Solution 4: Kill Existing Processes")
    print("Windows: taskkill /f /im python.exe")
    print("Mac/Linux: pkill -f streamlit")
    
    print("\\n🔧 Solution 5: Reinstall Streamlit")
    print("pip uninstall streamlit")
    print("pip install streamlit")
    
    print("\\n🔧 Solution 6: Use Virtual Environment")
    print("python -m venv venv")
    print("venv\\Scripts\\activate  # Windows")
    print("# source venv/bin/activate  # Mac/Linux")
    print("pip install streamlit")
    print("streamlit run streamlit_client.py")

def main():
    """Main diagnostic function"""
    print("🔍 Connection Diagnostic Tool")
    print("=" * 40)
    
    # Run all checks
    files_ok = check_streamlit_files()
    python_ok = check_python_environment()
    port_ok = check_port_availability(8501)
    streamlit_ok = test_streamlit_startup()
    
    print("\\n📊 Diagnostic Results:")
    print(f"Files: {'✅' if files_ok else '❌'}")
    print(f"Python: {'✅' if python_ok else '❌'}")
    print(f"Port 8501: {'✅' if port_ok else '❌'}")
    print(f"Streamlit: {'✅' if streamlit_ok else '❌'}")
    
    # Create working script
    create_working_startup_script()
    
    # Provide solutions
    provide_manual_solutions()
    
    print("\\n🎯 Recommended Next Steps:")
    print("1. Try: python start_guaranteed.py")
    print("2. If that fails, use manual solutions above")
    print("3. Or start components separately in two terminals")

if __name__ == "__main__":
    main()
