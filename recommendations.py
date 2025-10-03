# recommendations.py

_INSULT_WORDS = {
    "idiot": "person", "moron": "person", "stupid": "unhelpful",
    "dumb": "unclear", "retard": "person", "loser": "person",
    "ugly": "not nice", "fat": "overweight", "worthless": "not helpful",
}

_SEVERE_THREATS = {
    "kill yourself", "kys", "go die", "drink bleach", "hang yourself",
    "i will kill you", "i'll kill you", "i will find you", "i'll find you",
    "i will beat you", "i'll beat you", "i will hurt you", "i'll hurt you",
    "you're dead", "i hope you die",
}

def generate_recommendations(text: str, result: dict) -> dict:
    """Generates polite rewrite suggestions based on a set of rules."""
    original = text.strip()
    lowered = original.lower()

    is_toxic = result.get("label", "").lower() == "toxic"
    tox_score = float(result.get("probability", 0.0) or 0.0)
    cy_label = str(result.get("cyberbullying_label", "")).lower()

    suggestions = []
    polite = original  # Start with the original text

    # General guidance
    if is_toxic or tox_score >= 0.5:
        suggestions.append("Focus on the action or idea, not the person.")
        suggestions.append("Use first-person feelings (\"I feel\") instead of second-person blame (\"you are\").")
        suggestions.append("Replace absolute/harsh words with neutral or specific feedback.")
    if "!" in original:
        suggestions.append("Reduce exclamation marks to lower perceived aggression.")
    if any(phrase in lowered for phrase in ["you are", "you're", "u r", "you always", "you never"]):
        suggestions.append("Reframe from \"you\" statements to \"I\" statements (e.g., \"I think\").")

    # De-threaten
    is_severe_threat = any(p in lowered for p in _SEVERE_THREATS)
    if is_severe_threat:
        suggestions.append("Remove threats; state a boundary or request politely.")
        return {
            "suggestions": suggestions[:5],
            "polite_rewrite": "Expressing strong disagreement is okay, but threats are not. Please rephrase to state your point of view without threatening harm."
        }

    # --- Start the rewrite process ---
    # 1. Pronoun reframe: "you are" -> "I feel"
    if any(s in lowered for s in ["you are", "you're", "u r"]):
        for phrase in ["You are ", "you are ", "You're ", "you're ", "U r ", "u r "]:
            if phrase in polite:
                polite = polite.replace(phrase, "I feel that this is ", 1) # Replace only the first instance
                break

    # 2. Word-level softening for common insults
    tokens = polite.split()
    for i, tok in enumerate(tokens):
        key = tok.lower().strip(",.!?;:")
        if key in _INSULT_WORDS:
            tokens[i] = _INSULT_WORDS[key]
    polite = " ".join(tokens)

    # 3. Add a polite opening if the comment is still aggressive
    if is_toxic or cy_label.startswith("cyberbullying"):
        if not polite.lower().startswith(("please", "i think", "i feel", "could we", "let's")):
            polite = f"From my perspective, {polite[0].lower() + polite[1:]}" if polite else polite

    polite = " ".join(polite.split()) # Final cleanup for extra spaces

    return {"suggestions": suggestions[:5], "polite_rewrite": polite if polite and polite != original else ""}