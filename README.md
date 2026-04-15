<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.14-blue.svg?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Flask-Web_Framework-black.svg?style=for-the-badge&logo=flask">
  
  <h1>⚡ MAX Bot — Advanced AI Voice Assistant</h1>
  <p>A smart, browser-native voice assistant powered by Gemini 2.5 Flash, packed with modular tools and a beautiful glassmorphism interface.</p>
</div>

---

## ✨ Features Overview

MAX uses advanced Natural Language Processing to figure out what you want and dynamically selects the right tool for the job.

| Feature | Description |
|---|---|
| 🎙 **Native Voice Input** | Push-to-talk microphone and hands-free "Hey Max" wake word via modern Browser **Web Speech API** (Zero complex C++ `pyaudio` dependencies!). |
| 🔊 **Natural TTS** | Text-To-Speech read aloud seamlessly via browser-native natural voices. |
| 🤖 **Gemini 2.5 Flash AI** | Highly intelligent conversational agent powered by Google's latest Gemini architecture. |
| ▶️ **YouTube Interactive Gallery** | Searches YouTube and generates a horizontal, highly interactive scrollable gallery. Clicking a card instantly opens a built-in Modal Iframe player to watch the video *without leaving the chat*! |
| 🔍 **Intelligent Web Search** | Scrapes the web and routes the raw text back through Gemini for summarizing, so you get polished, conversational answers instead of link dumps. |
| 📧 **Multi-User Email** | Send emails directly from the chat. The UI features a slick modal allowing anyone using the app to securely enter their own SMTP credentials. |
| 🌤 **Live Weather** | Hooked up to OpenWeatherMap for instant, accurate forecasts anywhere. |
| 📈 **Live Stocks** | Hooked up to Yahoo Finance (`yFinance`) for instant stock and crypto tickers. |

## 🚀 Interactive UI Features
- **Glassmorphism Design:** Dark mode gradients, animated background orbs, blurring, and stunning visuals via `style.css`.
- **Quick Action Chips:** Tap the suggested bubbles on the home screen to instantly execute commands without typing.
- **Dynamic Modals:** Smooth pop-ups for composing Emails, entering Stock/City names, and watching YouTube videos.

---

## 🛠️ Setup & Installation

Because MAX now utilizes browser-native speech decoding, installation is incredibly fast and avoids the notoriously buggy `PyAudio`.

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Keys

Create a `.env` file in the main folder (you can copy `.env.example` as a template). 

```env
GEMINI_API_KEY=your_gemini_key       # Get from https://aistudio.google.com
WEATHER_API_KEY=your_owm_key         # Get from https://openweathermap.org/api

# (Optional) Default Server Email Config:
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password     # Use a Google App Password, NOT your real password
```
*Note: If users do not want to use the default `.env` server email, the front-end Email Modal allows them to inject their own temporary credentials when sending an email!*

### 3. Run Locally

```bash
python app.py
```
Go to `http://localhost:5000` in your web browser. 
*(Note: To use the Microphone, modern browsers require that you run via `localhost` or serve the application securely over `HTTPS`).*

---

## ☁️ Production Deployment

MAX Bot is pre-configured for cloud deployment!

We use **Gunicorn** as our production WSGI server. A `Procfile` is already included in the repo.
1. Push your repository to GitHub.
2. Link the repository to a free host like **Render.com** or **Heroku**.
3. Set your Build Command to: `pip install -r requirements.txt`
4. Make sure to input your `GEMINI_API_KEY` and `WEATHER_API_KEY` into your cloud provider's Environment Variables panel.
5. Deploy safely over HTTPS!

---

## 💬 Example Prompts to Try

* "Hey Max, what's the weather like in Tokyo right now?"
* "Get me the stock price for Nvidia (NVDA)"
* "Play lo-fi study girl music on YouTube" *(Watch the interactive gallery pop up!)*
* "Search the web for what happened to the Mars Opportunity Rover" *(Watch Gemini summarize the raw search!)*
* "Send an email to my friend"

---

## 🏗️ Architecture

- **Backend Logic:** Python 3.10+, Flask, Gunicorn
- **AI Engine:** Google `gemini-2.5-flash`
- **Tooling:** `yFinance`, `duckduckgo_search`, `smtplib`, native `urllib` scraping module.
- **Frontend & State:** Vanilla HTML/CSS/JS (Zero framework bloat), Web Speech API.
