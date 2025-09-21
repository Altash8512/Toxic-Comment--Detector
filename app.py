from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
from predict import predict_comment
from rewriter import generate_polite_rewrite, load_rewriter_if_available
from gemini_suggester import suggest_with_gemini
import os

app = Flask(__name__)
# CORS(app)

# Ensure template changes are picked up without restarting (dev use)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Lightweight fallback cyberbullying flagger (used only if backend model response lacks fields)
_CYBER_KEYWORDS = {
    "moron", "idiot", "dumb", "stupid", "loser", "retard",
    "kill yourself", "ugly", "fat", "worthless", "nobody likes you",
    "i will beat you", "i'll beat you", "i will find you", "i'll find you",
    "go die", "leave this group", "no one wants you",
}

def _augment_with_cyberbullying(result: dict, text: str) -> dict:
    if "cyberbullying_label" in result and "cyberbullying_score" in result:
        return result
    lowered = text.lower()
    is_bully = any(k in lowered for k in _CYBER_KEYWORDS)
    result["cyberbullying_label"] = "cyberbullying" if is_bully else "not cyberbullying"
    result["cyberbullying_score"] = 0.9 if is_bully else 0.1
    return result

# Lightweight ML-informed rewrite and guidance generator
_INSULT_WORDS = {
    "idiot": "person",
    "moron": "person",
    "stupid": "unhelpful",
    "dumb": "unclear",
    "retard": "person",
    "loser": "person",
    "ugly": "not nice",
    "fat": "overweight",
    "worthless": "not helpful",
}

def _generate_recommendations(text: str, result: dict) -> dict:
    original = text.strip()
    lowered = original.lower()

    is_toxic = result.get("label", "").lower() == "toxic"
    tox_score = float(result.get("probability", 0.0) or 0.0)
    cy_label = str(result.get("cyberbullying_label", "")).lower()
    cy_score = float(result.get("cyberbullying_score", 0.0) or 0.0)

    suggestions = []

    # General guidance
    if is_toxic or tox_score >= 0.5:
        suggestions.append("Avoid insults; describe the issue, not the person.")
        suggestions.append("Use first-person feelings (\"I feel\") instead of second-person blame (\"you are\").")
        suggestions.append("Replace absolute/harsh words with neutral or specific feedback.")
    if "!" in original:
        suggestions.append("Reduce exclamation marks to lower perceived aggression.")
    if any(phrase in lowered for phrase in ["you are", "you're", "u r", "you always", "you never"]):
        suggestions.append("Reframe from \"you\" statements to \"I\" statements (e.g., \"I think\").")

    # De-threaten
    if any(p in lowered for p in ["kill yourself", "go die", "i'll", "i will", "i will find you", "i'll find you", "beat you"]):
        suggestions.append("Remove threats; state a boundary or request politely.")

    # Word-level softening
    tokens = original.split()
    softened_tokens = []
    for tok in tokens:
        key = tok.lower().strip(",.!?;:")
        replacement = _INSULT_WORDS.get(key)
        softened_tokens.append(replacement if replacement else tok)
    softened = " ".join(softened_tokens)

    # Pronoun reframe: you -> I/we (very conservative)
    softened_lower = softened.lower()
    if any(s in softened_lower for s in ["you are", "you're"]):
        softened = softened.replace("You are ", "I feel ")
        softened = softened.replace("you are ", "I feel ")
        softened = softened.replace("You're ", "I feel ")
        softened = softened.replace("you're ", "I feel ")

    # Add hedging if very high score
    polite = softened
    if is_toxic or cy_label.startswith("cyberbullying") or max(tox_score, cy_score) >= 0.7:
        if not polite.lower().startswith(("please", "i think", "i feel", "could we", "let's")):
            polite = f"I think {polite[0].lower() + polite[1:]}" if polite else polite

    # Final cleanups
    polite = polite.replace("  ", " ").strip()

    return {
        "suggestions": suggestions[:5],
        "polite_rewrite": polite if polite and polite != original else "",
    }

# Allow requests from any origin (frontend, browser, extension)
# CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Text input is missing"}), 400

    print("🔍 Received text:", data["text"])
    result = predict_comment(data["text"])
    # Ensure cyberbullying fields are present for the UI
    result = _augment_with_cyberbullying(result, data["text"])
    # Generate ML-informed, rules-based recommendations
    # Try Kaggle-trained rewriter if available; otherwise use rules
    polite = generate_polite_rewrite(data["text"]) or ""
    rec = _generate_recommendations(data["text"], result)
    if polite:
        rec["polite_rewrite"] = polite
    # Gemini suggestions appended after ML suggestions
    gem = suggest_with_gemini(data["text"])
    result.update(rec)
    result.update(gem)
    print("✅ Sending result:", result)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses dynamic port
    app.run(debug=False, host='0.0.0.0', port=port)
