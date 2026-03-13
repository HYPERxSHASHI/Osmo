# OSMO - Personal AI Assistant (Python)

OSMO is a local desktop AI assistant inspired by JARVIS-style interaction. It includes:

- Voice wake phrase: **"Hey Osmo"**
- Response line: **"What happened sir, do you need something?"**
- GUI in **white + chocolate brown** style
- Voice + typed command support
- Common actions: time/date, open apps, open websites, search Google
- Optional terminal command execution with a safety confirmation popup

## Important Safety Note
This project runs locally and can execute commands **only when you explicitly allow it**.
Giving any AI unrestricted, silent "full access" to your computer is unsafe.

## 1) Install Python
Install Python 3.10+ from [python.org](https://www.python.org/downloads/).
While installing on Windows, enable **"Add Python to PATH"**.

## 2) Install dependencies
In terminal (inside this folder):

```bash
pip install -r requirements.txt
```

If `pyaudio` fails on Windows, run:

```bash
pip install pipwin
pipwin install pyaudio
```

## 3) Run OSMO

```bash
python osmo.py
```

Or just double-click:

- `run_osmo.bat`

## 4) Voice usage
1. Click **Start Listening**
2. Say: **Hey Osmo**
3. Then say command examples:
   - "time"
   - "date"
   - "open notepad"
   - "search iron man suit"
   - "run command ipconfig"

## Notes
- Microphone permission must be allowed.
- Some app-opening commands are Windows-focused (Notepad/Calc/CMD/PowerShell).
- You can extend `execute_command()` in `osmo.py` with more skills.
