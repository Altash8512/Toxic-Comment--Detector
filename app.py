from flask import Flask, request, jsonify, render_template
from gemini_suggester import suggest_with_gemini
from config import get_classification_from_keywords
from recommendations import generate_recommendations
import os

app = Flask(__name__)

# Ensure template changes are picked up without restarting (dev use)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Text input is missing"}), 400

    print(f"🔍 Received text: '{data['text']}' with context: '{data.get('context', 'None')}'")
    # Using keyword-based classification since local models are disabled
    result = get_classification_from_keywords(data["text"], data.get("context"))
    
    # --- Recommendation Logic: Prioritize Gemini, fall back to local rules ---
    # 1. Attempt to get high-quality suggestions from Gemini first.
    gem = suggest_with_gemini(data["text"], data.get("context"))
    
    # 2. If Gemini fails or returns no content, use the local rules-based fallback.
    if gem.get("gemini_tips") or gem.get("gemini_rewrite"):
        print("✨ Using suggestions from Gemini API.")
        # Use Gemini's output for the main recommendation fields.
        result["suggestions"] = gem.get("gemini_tips", [])
        result["polite_rewrite"] = gem.get("gemini_rewrite", "")
    else:
        print("⚠️ Gemini failed or returned no content. Using local rules-based fallback.")
        # Fallback to the local, rules-based generator.
        rec = generate_recommendations(data["text"], result)
        result.update(rec)
        
    print("✅ Sending result:", result)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses dynamic port
    app.run(debug=False, host='0.0.0.0', port=port)
