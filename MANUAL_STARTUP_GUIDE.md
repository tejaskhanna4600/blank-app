# Manual Startup Guide for Streamlit Issues

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
   - Windows: `venv\Scripts\activate`
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
