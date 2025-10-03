import os
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions
from config import HINGLISH_KEYWORDS


def _configure() -> bool:
    # Load environment variables from a .env file if it exists
    # This is great for local development.
    load_dotenv()

    # Load the API key from an environment variable for security
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Only print this once to avoid spamming logs
        print("[Gemini] ⚠️  GEMINI_API_KEY environment variable not set. Gemini suggestions will be disabled.")
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


def suggest_with_gemini(text: str, context: str = None) -> Dict[str, Any]:
    """Return a dict with keys: gemini_tips (list[str]), gemini_rewrite (str)."""
    if not _configure():
        return {"gemini_tips": [], "gemini_rewrite": ""}

    # A list of free-tier models to try in order. If the first one hits a rate limit,
    # the code will automatically fall back to the next one.
    models_to_try = ["gemini-pro-latest", "gemini-flash-latest"]
    
    context_prompt = ""
    if context:
        context_prompt = f"The user is replying to the following comment: \"{context.strip()}\".\n"
    
    # --- Dynamic Language for Rewrite ---
    is_hinglish = any(word in text.lower() for word in HINGLISH_KEYWORDS)
    if is_hinglish:
        rewrite_language_instruction = "Provide one polite rewrite in Hinglish (Hindi written in English script). For example, if the input is 'tu idiot hai', the rewrite could be 'Aapki baat samajh nahi aayi'."
    else:
        rewrite_language_instruction = "Provide one polite rewrite in simple English."

    prompt = (
        "You are a content detox assistant. The user's message may be in English or Hinglish (Hindi written in English script). "
        "Suggest up to 5 concise tips in simple English. "
        f"{rewrite_language_instruction} "
        f"{context_prompt}"
        "Respond ONLY as strict JSON: {\"tips\": string[], \"rewrite\": string}.\n\n"
        f"Message: {text.strip()}"
    )
    print(f"[Gemini] Using prompt:\n{prompt}")
    for model_name in models_to_try:
        try:
            print(f"[Gemini] Attempting to use model: {model_name}")
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt)
            content = getattr(resp, "text", None)
            parsed = _extract_json(content or "")
            return {
                "gemini_tips": [t for t in (parsed.get("tips") or []) if isinstance(t, str)][:5],
                "gemini_rewrite": parsed.get("rewrite") or "" if isinstance(parsed.get("rewrite"), str) else "",
            }
        except exceptions.ResourceExhausted as e:
            print(f"[Gemini] ⚠️  Rate limit likely reached for {model_name}. Trying next model...")
            continue # Move to the next model in the list

        except Exception as e:
            # For other errors (like invalid API key, model not found), stop trying.
            print(f"[Gemini] ❌ An unexpected error occurred with {model_name}: {e}")
            break # Exit the loop

    # If all models fail, return an empty result.
    print("[Gemini] All models failed or were rate-limited. Returning empty result.")
    return {"gemini_tips": [], "gemini_rewrite": ""}
