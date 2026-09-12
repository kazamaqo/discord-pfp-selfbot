# Discord PFP Selfbot 🖼️

A simple Discord selfbot to quickly change your profile picture.

## Setup

### 1. Install Python (if using Termux)
```bash
pkg install python pip git
```

### 2. Clone the repo
```bash
git clone https://github.com/kazamaqo/discord-pfp-selfbot.git
cd discord-pfp-selfbot
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

Run the bot:
```bash
python bot.py
```

It will ask for your Discord token - paste it and press Enter.

### Change your PFP
1. Upload an image with the command:
```
>pfp [image]
```

2. The bot will change your profile picture instantly!

## ⚠️ Warning
- This is a **selfbot** (uses your personal account)
- Selfbots violate Discord ToS - use at your own risk
- Never share your token with anyone

## How to get your token
1. Open Discord
2. Press `Ctrl+Shift+I` (DevTools)
3. Go to Application → Local Storage → https://discord.com
4. Find `token` key and copy the value (remove quotes)

---

Made with ❤️
