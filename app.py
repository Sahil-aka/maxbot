import json
import queue
import threading
import logging
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Initialize core modules gracefully ---
try:
    from bot.assistant import Assistant
    assistant = Assistant()
    logger.info("Assistant initialized.")
except Exception as e:
    logger.error(f"Assistant init failed: {e}")
    assistant = None

try:
    from bot.speech import SpeechHandler
    speech = SpeechHandler()
    logger.info("Speech handler initialized.")
except Exception as e:
    logger.warning(f"Speech handler unavailable: {e}")
    speech = None

wake_queues: dict[str, queue.Queue] = {}


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400
    if not assistant:
        return jsonify({"error": "Assistant not available. Check your .env configuration."}), 503
    try:
        response = assistant.process(query)
        return jsonify({"query": query, "response": response, "success": True})
    except Exception as e:
        logger.error(f"/ask error: {e}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/listen", methods=["POST"])
def listen():
    if not speech or not speech._sr_available:
        return jsonify({"error": "Voice input unavailable. Install PyAudio to enable microphone support."}), 503
    try:
        text = speech.listen_once()
        if not text:
            return jsonify({"error": "Could not understand audio. Please speak clearly and try again.", "success": False})
        response = assistant.process(text) if assistant else "Assistant unavailable."
        return jsonify({"query": text, "response": response, "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/speak", methods=["POST"])
def speak():
    if not speech or not speech._tts_available:
        return jsonify({"status": "tts_unavailable"})
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if text:
        threading.Thread(target=speech.speak, args=(text,), daemon=True).start()
    return jsonify({"status": "speaking"})


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json(silent=True) or {}
    to_addr = data.get("to", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()
    sender_email = data.get("sender_email", "").strip()
    sender_password = data.get("sender_password", "").strip()
    
    if not all([to_addr, subject, body]):
        return jsonify({"error": "Please fill in all required fields (To, Subject, Message)."}), 400
    try:
        from bot.tools.email_tool import send_email as _send
        result = _send(to_addr, subject, body, from_address=sender_email, password=sender_password)
        return jsonify({"response": result, "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/clear", methods=["POST"])
def clear():
    if assistant:
        assistant.clear_memory()
    return jsonify({"status": "cleared"})


@app.route("/wake-status")
def wake_status():
    client_id = request.args.get("client_id", "default")
    if client_id not in wake_queues:
        wake_queues[client_id] = queue.Queue()
    q = wake_queues[client_id]

    def generate():
        try:
            while True:
                try:
                    event = q.get(timeout=20)
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except GeneratorExit:
            pass

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/toggle-wake-word", methods=["POST"])
def toggle_wake_word():
    if not speech or not speech._sr_available:
        return jsonify({"error": "Voice input unavailable. Install PyAudio.", "success": False}), 503
    data = request.get_json(silent=True) or {}
    enabled = data.get("enabled", False)
    client_id = data.get("client_id", "default")
    if client_id not in wake_queues:
        wake_queues[client_id] = queue.Queue()
    if enabled:
        speech.start_wake_word_listener(wake_queues[client_id], assistant)
    else:
        speech.stop_wake_word_listener()
    return jsonify({"status": "ok", "enabled": enabled, "success": True})


if __name__ == "__main__":
    print("\n🚀  MAX Bot is starting...")
    print("🌐  Open your browser at: http://localhost:5000\n")
    app.run(debug=True, threaded=True, host="0.0.0.0", port=5000)
