import os
from typing import Dict, Any

import google.generativeai as genai


def _configure() -> bool:
    # --- Direct API Key ---
    # Load the API key securely from an environment variable.
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True


def _extract_json(text: str) -> Dict[str, Any]:
    import json
    if not text:
        return {}
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to extract JSON segment
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end+1]
        try:
            return json.loads(snippet)
        except Exception:
            return {}
    return {}


def suggest_with_gemini(text: str) -> Dict[str, Any]:
    """Return a dict with keys: gemini_tips (list[str]), gemini_rewrite (str)."""
    if not _configure():
        return {"gemini_tips": [], "gemini_rewrite": ""}

    prompt = (
        "You are a content detox assistant. Given the user's message, "
        "suggest up to 5 concise tips to reduce toxicity and provide one polite rewrite. "
        "Respond ONLY as strict JSON: {\"tips\": string[], \"rewrite\": string}.\n\n"
        f"Message: {text.strip()}"
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        resp = model.generate_content(prompt)
        content = getattr(resp, "text", None)
        parsed = _extract_json(content or "")
        tips = parsed.get("tips") or []
        rewrite = parsed.get("rewrite") or ""
        tips = [t for t in tips if isinstance(t, str)][:5]
        rewrite = rewrite if isinstance(rewrite, str) else ""
        return {"gemini_tips": tips, "gemini_rewrite": rewrite}
    except Exception as e:
        # Surface minimal signal for debugging in server logs
        try:
            print("[Gemini] suggestion error:", str(e))
        except Exception:
            pass
        return {"gemini_tips": [], "gemini_rewrite": ""}
