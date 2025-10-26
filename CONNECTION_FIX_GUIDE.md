# 🔧 Fix "Localhost Refused to Connect" Error

## 🚨 Quick Diagnosis
Run this first to identify the exact problem:
```bash
python diagnose_connection.py
```

## 🎯 Most Common Solutions

### **Solution 1: Start Components Separately (Recommended)**
Open **TWO separate terminals**:

**Terminal 1 (Pygame Game):**
```bash
python main.py
```

**Terminal 2 (Streamlit Web Interface):**
```bash
streamlit run streamlit_client.py --server.port 8501
```

Then open browser: http://localhost:8501

### **Solution 2: Use Different Port**
If port 8501 is busy:
```bash
streamlit run streamlit_client.py --server.port 8502
```
Access: http://localhost:8502

### **Solution 3: Check What's Using Port 8501**
**Windows:**
```bash
netstat -an | findstr 8501
```

**Mac/Linux:**
```bash
lsof -i :8501
```

If something is using the port, kill it:
**Windows:**
```bash
taskkill /f /im python.exe
```

**Mac/Linux:**
```bash
pkill -f streamlit
```

### **Solution 4: Fix Streamlit Installation**
```bash
pip uninstall streamlit
pip install streamlit
```

### **Solution 5: Use Guaranteed Startup Script**
```bash
python start_guaranteed.py
```

## 🔍 Step-by-Step Troubleshooting

### **Step 1: Check if Streamlit is Running**
Look for any terminal windows with Streamlit output. If none, Streamlit isn't running.

### **Step 2: Check Browser**
- Try different browser
- Clear browser cache
- Try incognito/private mode
- Try http://127.0.0.1:8501 instead of localhost

### **Step 3: Check Firewall**
- Windows: Allow Python through Windows Firewall
- Mac: System Preferences > Security & Privacy > Firewall
- Linux: Check iptables rules

### **Step 4: Check Antivirus**
Some antivirus software blocks localhost connections. Temporarily disable to test.

### **Step 5: Use Command Line Test**
```bash
curl http://localhost:8501
```
If this fails, the issue is with Streamlit not running.

## 🎮 Alternative: Play Without Web Interface

If Streamlit continues to fail, you can still play:

```bash
python main.py
```

**Keyboard Controls:**
- **R**: Roll dice
- **B**: Buy property  
- **E**: End turn
- **S**: Sell property
- **T**: Start trading
- **U**: Undo move

## 🚀 Quick Fix Commands

**Kill all Python processes and restart:**
```bash
# Windows
taskkill /f /im python.exe
python main.py

# Mac/Linux  
pkill -f python
python main.py
```

**Start Streamlit with verbose output:**
```bash
streamlit run streamlit_client.py --server.port 8501 --logger.level debug
```

**Check if Streamlit is installed:**
```bash
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

## 📞 Still Having Issues?

1. **Run the diagnostic script**: `python diagnose_connection.py`
2. **Check the error messages** in the terminal where you started Streamlit
3. **Try the guaranteed startup script**: `python start_guaranteed.py`
4. **Use manual startup** (two separate terminals)

The most reliable method is starting the components separately in two terminals!
