# ⚡ MAX Bot — AI Voice Assistant

> A voice-controlled AI assistant built with Python, Flask, Gemini AI, and a sleek glassmorphism web UI.

## Features

| Feature | Description |
|---|---|
| 🎙 **Voice Input** | Push-to-talk microphone via `SpeechRecognition` |
| 🔊 **Text-to-Speech** | Natural voice responses via `pyttsx3` |
| 👂 **Wake Word** | Hands-free activation with "Hey Max" |
| 🤖 **Gemini AI** | Conversational AI powered by Google Gemini + LangChain |
| 🌤 **Weather** | Real-time weather via OpenWeatherMap API |
| 📈 **Stocks** | Live stock prices via yFinance |
| ▶️ **YouTube** | Video search and playback links |
| 📧 **Email** | Send emails via Gmail SMTP |
| 🔍 **Web Search** | DuckDuckGo search (no API key needed) |

## Setup

### 1. Install Dependencies

> **Windows users:** PyAudio requires a special installation step.

```bash
pip install pipwin
pipwin install pyaudio
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
copy .env.example .env
```

Edit `.env` and fill in your keys:

```env
GEMINI_API_KEY=your_gemini_key       # https://aistudio.google.com
WEATHER_API_KEY=your_owm_key         # https://openweathermap.org/api
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password     # Gmail App Password (not regular password)
```

#### Getting a Gmail App Password:
1. Enable 2FA at [myaccount.google.com](https://myaccount.google.com) → Security
2. Go to Security → **App passwords**
3. Create a password for "Mail" and paste it as `EMAIL_PASSWORD`

### 3. Run

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

## Usage

- **Type** a query in the input box and press Enter or click Send
- **Click the mic button** (🎤) to use push-to-talk voice input
- **Toggle "Hey Max"** in the header to enable hands-free wake word detection
- Use **Quick Actions** (Weather / Stocks / YouTube / Email / Search) for fast access
- **Suggestion chips** on the welcome screen for quick demos

## Example Commands

```
What's the weather in New Delhi?
Get the stock price of Nvidia
Play Blinding Lights on YouTube
Search for latest AI news
Send email to john@example.com
Tell me a joke
What is quantum computing?
```

## Tech Stack

- **Backend:** Python 3.10+, Flask
- **AI:** Google Gemini 1.5 Flash (via LangChain)
- **Speech:** SpeechRecognition (Google Web Speech), pyttsx3, PyAudio
- **Data:** yFinance, OpenWeatherMap, youtube-search-python, DuckDuckGo Search
- **Frontend:** Vanilla HTML/CSS/JS — Dark glassmorphism UI, Google Fonts (Outfit)
