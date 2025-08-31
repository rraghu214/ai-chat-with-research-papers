import os
import re
import uuid
from functools import lru_cache
from flask import Flask, render_template, request, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix

from extractors import extract_text_from_url
from llm import summarize_map_reduce, chat_answer

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# Simple in-memory caches (OK for a demo; consider Redis in production)
DOC_CACHE = {}          # key: url -> {"text": str, "summaries": {"LOW": str, ...}}
CHAT_HISTORY = {}       # key: (session_id, url) -> list of {"role": "user"|"model", "text": str}

VALID_LEVELS = {"LOW", "MEDIUM", "HIGH"}

@app.before_request
def ensure_session():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    url = request.form.get("paper_url", "").strip()
    level = request.form.get("complexity", "LOW").strip().upper()
    if level not in VALID_LEVELS:
        level = "LOW"

    if not (url.startswith("http://") or url.startswith("https://")):
        return render_template("index.html", error="Please enter a valid http(s) URL.")

    try:
        if url not in DOC_CACHE:
            text = extract_text_from_url(url)
            if not text or len(text.strip()) < 200:
                return render_template("index.html", error="Could not extract enough text from the provided URL.")
            DOC_CACHE[url] = {"text": text, "summaries": {}}
        else:
            text = DOC_CACHE[url]["text"]

        # Generate summary (cached per level)
        if level not in DOC_CACHE[url]["summaries"]:
            summary = summarize_map_reduce(text, level=level)
            DOC_CACHE[url]["summaries"][level] = summary
        else:
            summary = DOC_CACHE[url]["summaries"][level]

        # Initialize chat history for this paper in this session
        sid = session["sid"]
        key = (sid, url)
        if key not in CHAT_HISTORY:
            CHAT_HISTORY[key] = []

        return render_template(
            "index.html",
            paper_url=url,
            level=level,
            summary=summary,
        )
    except Exception as e:
        return render_template("index.html", error=f"Error: {e}")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    url = data.get("paper_url", "").strip()
    message = data.get("message", "").strip()
    if not url or not message:
        return jsonify({"ok": False, "error": "Missing url or message"}), 400

    if url not in DOC_CACHE:
        return jsonify({"ok": False, "error": "Please summarize the paper first."}), 400

    sid = session.get("sid")
    key = (sid, url)
    history = CHAT_HISTORY.setdefault(key, [])

    # Add user message
    history.append({"role": "user", "text": message})

    try:
        # Answer with LLM using the paper text as context + history
        text_context = DOC_CACHE[url]["text"]
        answer = chat_answer(text_context, history)
        history.append({"role": "model", "text": answer})
        return jsonify({"ok": True, "answer": answer})
    except Exception as e:
        history.pop()  # rollback last user msg if failed
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")