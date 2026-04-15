import os
import threading
import logging

logger = logging.getLogger(__name__)


class SpeechHandler:
    def __init__(self):
        self._wake_listening = False
        self._wake_thread = None
        self._tts_lock = threading.Lock()
        self._tts_available = False
        self._sr_available = False
        self._init_tts()
        self._check_sr()

    def _init_tts(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty("voices")
            if voices:
                for v in voices:
                    if any(k in v.name.lower() for k in ["zira", "david", "hazel", "english"]):
                        self.engine.setProperty("voice", v.id)
                        break
            self.engine.setProperty("rate", 170)
            self.engine.setProperty("volume", 0.9)
            self._tts_available = True
        except Exception as e:
            logger.warning(f"TTS unavailable: {e}")
            self.engine = None

    def _check_sr(self):
        try:
            import speech_recognition as sr  # noqa: F401
            import pyaudio  # noqa: F401
            self._sr_available = True
        except ImportError:
            logger.warning("SpeechRecognition or PyAudio not available. Voice input disabled.")

    def speak(self, text: str):
        if not self._tts_available:
            return
        # Strip markdown for TTS
        clean = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
        with self._tts_lock:
            try:
                self.engine.say(clean)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")

    def listen_once(self):
        if not self._sr_available:
            return None
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=10, phrase_time_limit=15)
                text = r.recognize_google(audio)
                return text.lower().strip()
        except Exception as e:
            logger.warning(f"Listen error: {type(e).__name__}: {e}")
            return None

    def start_wake_word_listener(self, event_queue, assistant):
        if self._wake_listening or not self._sr_available:
            return
        self._wake_listening = True
        self._wake_thread = threading.Thread(
            target=self._wake_loop, args=(event_queue, assistant), daemon=True
        )
        self._wake_thread.start()

    def stop_wake_word_listener(self):
        self._wake_listening = False

    def _wake_loop(self, event_queue, assistant):
        import speech_recognition as sr
        r = sr.Recognizer()
        WAKE_PHRASES = ["hey max", "hi max", "hello max", "ok max", "okay max"]

        while self._wake_listening:
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.2)
                    try:
                        audio = r.listen(source, timeout=3, phrase_time_limit=4)
                        text = r.recognize_google(audio).lower()
                        if any(w in text for w in WAKE_PHRASES):
                            event_queue.put({"type": "wake_detected"})
                            command = self.listen_once()
                            if command:
                                response = assistant.process(command)
                                event_queue.put({
                                    "type": "command",
                                    "query": command,
                                    "response": response,
                                })
                                threading.Thread(
                                    target=self.speak, args=(response,), daemon=True
                                ).start()
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        pass
            except Exception:
                import time
                time.sleep(1)
