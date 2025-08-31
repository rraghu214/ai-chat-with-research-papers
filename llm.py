import os
import math
from typing import List, Dict
from google import genai

# Model selection
# Defaults to Gemini Flash 2.x name. You can change via GEMINI_MODEL env var.
# If you have access to a specific preview like "gemini-2.5-flash", set it there.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY env var is required")

client = genai.Client(api_key=GEMINI_API_KEY)

# -------------- Prompt helpers --------------
from prompts import CHUNK_SUMMARY_PROMPT, REDUCE_SUMMARY_PROMPT, CHAT_PROMPT


def _call_gemini(contents: List[Dict]) -> str:
    """Low-level call using client.models.generate_content; returns text."""
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
    )
    # The SDK exposes either resp.output_text or resp.text depending on version
    text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
    if not text:
        # Fallback: attempt to construct from candidates
        try:
            return resp.candidates[0].content.parts[0].text
        except Exception:
            return str(resp)
    return text


def _split_text(text: str, max_chars: int = 20000, overlap: int = 800) -> List[str]:
    """Simple word-safe chunking to keep prompts reasonably sized."""
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    chunks = []
    cur = []
    cur_len = 0
    for w in words:
        lw = len(w) + 1
        if cur_len + lw > max_chars:
            chunks.append(" ".join(cur))
            # start new with overlap from tail
            tail = " ".join(cur)[-overlap:]
            cur = [tail]
            cur_len = len(tail)
        cur.append(w)
        cur_len += lw
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def summarize_map_reduce(full_text: str, level: str = "LOW") -> str:
    """Map-reduce summarization across chunks with a final synthesis.
    level in {LOW, MEDIUM, HIGH}
    """
    chunks = _split_text(full_text)

    # 1) Map step: per-chunk summaries
    partials: List[str] = []
    for i, chunk in enumerate(chunks, 1):
        prompt = CHUNK_SUMMARY_PROMPT.format(level=level, chunk=chunk)
        contents = [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
        partial = _call_gemini(contents)
        partials.append(partial)

    # 2) Reduce step: synthesize into a single coherent summary at the same level
    reduce_prompt = REDUCE_SUMMARY_PROMPT.format(level=level, partials="\n\n".join(partials))
    contents = [
        {"role": "user", "parts": [{"text": reduce_prompt}]}
    ]
    final_summary = _call_gemini(contents)
    return final_summary


def chat_answer(doc_text: str, history: List[Dict[str, str]], max_context_chars: int = 60000) -> str:
    """Answer a user question grounded in doc_text and chat history.

    history: list of {role: 'user'|'model', text: str}
    """
    # Trim document context to fit prompt size
    context = doc_text[:max_context_chars]

    # Build contents from history + current user question (last item is user)
    contents: List[Dict] = []

    # Add system-like instruction by putting it in the first user message
    system_user_message = CHAT_PROMPT.format(context=context)
    contents.append({"role": "user", "parts": [{"text": system_user_message}]})

    for turn in history:
        contents.append({"role": turn["role"], "parts": [{"text": turn["text"]}]})

    return _call_gemini(contents)