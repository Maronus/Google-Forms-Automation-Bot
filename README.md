# Google Forms Automation Bot (Maronus)

```text
    █▄ ▄█ ▄▀▀▀▄ █▀▀▀▄ ▄▀▀▀▄ █▄  █ █   █ ▄▀▀▀ 
    █ ▀ █ █▀▀▀█ █▀▀█  █   █ █ ▀▄█ █   █  ▀▀▀▄
    ▀   ▀ ▀   ▀ ▀   ▀  ▀▀▀  ▀   ▀  ▀▀▀   ▀▀▀ 
    google forms automation  @maronus
```

A minimal, command-line Google Forms automation tool that simulates bulk human responses and bypasses rate limits. 

## > The Backstory
I made this project because in school they did not let us see the exam results unless we submit at least 50 responses on a feedback form, and my colleagues were lazy and not helping. Instead of waiting for them, I built this script to automate the process and get past the requirement.

### > Why is there an encrypted version?
I didn't want any of my colleagues to take the source code, monetize the script, and sell it to other students. Therefore, I built a custom encryption tool to pack the source code into an encrypted payload.

## Features
- **Linked Distribution System:** Creates consistent "Virtual Users" to ensure logically flawless submissions without contradictions.
- **Human-like Delays:** Supports regular or irregular delay timers between responses.
- **RTL Support:** Full terminal support for right-to-left languages (Arabic, Hebrew).
- **Zero Config:** Automatically installs required dependencies on any system, including Android's Termux.

### > How does the Linked System work?
1. **Create Virtual Users:** The script reserves slots for the total number of responses you want.
2. **Distribute Question 1:** Answers are assigned top-to-bottom.
3. **Distribute Question 2:** The next set of answers aligns with the previous ones, so User 1's profile stays perfectly consistent.
4. **The Final Shuffle:** Once all profiles are built, the script shuffles them like a deck of cards. 
5. **Submission:** The responses are sent in this new randomized order so Google doesn't detect a sequential pattern.

## How to Run (One Command)
Run this command in your terminal to instantly download and launch the bot:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/Maronus/Google-Forms-Automation-Bot/main/src/google_forms_bot.py -OutFile google_forms_bot.py ; python google_forms_bot.py
```

**Windows (CMD) / Linux / macOS / Termux:**
```bash
curl -sO https://raw.githubusercontent.com/Maronus/Google-Forms-Automation-Bot/main/src/google_forms_bot.py && python3 google_forms_bot.py
```

*(Note: The downloadable script is encrypted to prevent resale by third parties. The full source code is available in the `src/` folder for developers).*

---

## > Disclaimer
This script is intended for educational purposes only. Do not use it to spam or abuse services.
