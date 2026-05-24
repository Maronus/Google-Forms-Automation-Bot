# Google Forms Automation Bot (Maronus)

A minimal, command-line Google Forms automation tool that simulates bulk human responses and bypasses rate limits. Built to quickly bypass "minimum response" requirements in school.

## Features
- **Linked Distribution System:** Creates consistent "Virtual Users" to ensure logically flawless submissions without contradictions.
- **Human-like Delays:** Supports regular or irregular delay timers between responses.
- **RTL Support:** Full terminal support for right-to-left languages (Arabic, Hebrew).
- **Zero Config:** Automatically installs required dependencies on any system, including Android's Termux.

## How to Run (One Command)
Run this command in your terminal to instantly download and launch the bot:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/Maronus/Google-Forms-Automation-Bot/main/src/google_forms_bot.py -OutFile google_forms_bot.py ; python google_forms_bot.py
```

**Windows (CMD) / Linux / macOS / Termux:**
```bash
curl -O https://raw.githubusercontent.com/Maronus/Google-Forms-Automation-Bot/main/src/google_forms_bot.py && python google_forms_bot.py
```

*(Note: The downloadable script is encrypted to prevent resale by third parties. The full source code is available in the `src/` folder for developers).*
