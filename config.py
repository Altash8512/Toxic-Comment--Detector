# config.py

"""
This file contains the configuration for the keyword-based classification.
You can add or remove words from these lists to customize the detector's
sensitivity and specificity for 'toxic' and 'cyberbullying' comments.
"""

# ==============================================================================
# CLASSIFICATION HIERARCHY:
# 1. SEVERE_OVERLAP_WORDS: Checked first. Flags comment as BOTH toxic and cyberbullying.
# 2. CYBERBULLYING_WORDS: Checked second. Flags comment as ONLY cyberbullying.
# 3. TOXIC_WORDS: Checked last. Flags comment as ONLY toxic.
# ==============================================================================

# 1. SEVERE_OVERLAP_WORDS (Both Toxic & Cyberbullying)
# These are the most harmful words, representing direct threats or severe slurs
# that are considered both a personal attack and generally toxic.
SEVERE_OVERLAP_WORDS = {
    # Threats & Harmful Suggestions
    "kill yourself", "kys", "go die", "drink bleach", "hang yourself",
    "i will kill you", "i'll kill you", "i will find you", "i'll find you",
    "i will beat you", "i'll beat you", "i will hurt you", "i'll hurt you",
    "watch your back", "you're dead", "i hope you die",
    "i will end you", "i'll end you", "you should disappear", "go play in traffic",
    "i'm coming for you", "i know where you live",

    # Severe Slurs, Insults & Hate Speech (often directed)
    "cunt", "faggot", "dyke", "tranny", "whore", "slut", "bitch",
    "asshole", "dickhead", "bastard", "son of a bitch", "fuck you",
    "nigger", "nigga", "chink", "spic", "retard", "retarded", "beaner", "coon",
    "u are a bitch", "u r a bitch", "you are a whore", "you're a slut",
    "eat shit and die",

    # Hinglish Severe Slurs & Insults
    "madarchod", "bhenchod", "bhen ke lode", "bsdk", "bkl", "chutiye", "gandu",
    "teri maa ki", "teri maa ka", "randi", "gaandu", "mc", "bc", "mkl",
}

# 2. CYBERBULLYING_WORDS (Cyberbullying, but not general profanity)
# These are personal attacks, insults, or social exclusion terms.
CYBERBULLYING_WORDS = {
    # Insults & Personal Attacks
    "idiot", "moron", "stupid", "dumb", "retard", "loser", "imbecile", "fool",
    "worthless", "pathetic", "useless", "noob", "freak", "weirdo", "lame", "clown", "buffoon",
    "ugly", "fat", "hideous", "disgusting", "repulsive", "pimpleface", "scum", "vermin",
    "four-eyes", "nerd", "geek", "dork", "spaz", "brain-dead", "brainless", "airhead",
    "you're an embarrassment", "you are an embarrassment", "you're a disgrace",

    # Threats & Harmful Suggestions (less severe than OVERLAP)
    "uninstall life", "unalive", "go commit die", "go touch a live wire",

    # Social Exclusion & Harassment
    "nobody likes you", "no one wants you", "go away", "leave us alone",
    "everyone hates you", "you have no friends", "outcast", "loner",
    "creep", "stalker", "pervert", "you don't belong here", "get out", "stay away from me",
    "you're not welcome", "we don't want you here",

    # Mocking & Belittling
    "crybaby", "snowflake", "wimp", "coward", "sissy", "manchild",
    "you're a joke", "so triggered", "get a life", "touch grass", "stay mad",
    "grow up", "get over it", "you're so sensitive", "you are a joke", "cope harder",
    "skill issue", "ez", "get good", "gg ez", "owned", "pwned", "rekt",
    "imagine being you", "ratio", "L", "take the L", "hold this L",
    "who asked", "nobody asked", "did I ask", "and?", "ok and?",
    "are you crying", "u mad bro", "you mad?", "salty", "stay salty",
    "what a child", "such a baby", "you're pathetic",
    "mald", "seethe", "mald and seethe",

    # Hinglish Insults & Mocking
    "chutiya", "saala", "kutta", "kuttiya", "pagal", "bewakoof",
    "bakwaas band kar", "chup kar", "kamina", "harami", "nalayak", "gadha",
    "ullu ka pattha", "dimag kharab hai", "nikal", "chal nikal",
}


# ==============================================================================
# These words are checked ONLY IF no cyberbullying words were found.
# They represent general toxicity, frustration, or negativity that isn't a
# direct personal attack or threat.
# ==============================================================================

TOXIC_WORDS = {
    # Profanity & Strong Language (not already in cyberbullying)
    "fuck", "shit", "damn", "hell", "piss", "crap", "ass", "dick", "douche",
    "motherfucker", "fucking", "shitty", "dammit", "goddamn", "bloody", "bugger", "bollocks",

    # Aggressive & Hostile Language
    "hate", "despise", "detest", "abhor", "loathe",
    "awful", "terrible", "horrible", "garbage", "trash", "crap", "rubbish",
    "sucks", "blows", "is the worst", "is terrible", "is awful", "dogwater", "hot garbage",
    "bullshit", "bs", "nonsense", "ridiculous", "insane", "crazy", "delusional", "unhinged",
    "what the hell", "what the fuck", "wtf", "stfu", "piss off", "shut up", "gtfo", "fuck off",
    "go to hell", "burn in hell",

    # Hinglish Frustration
    "bakwaas", "kya bakwaas hai", "abe", "hatt", "chal hatt", "kya musibat hai",

    # Frustration & Anger
    "furious", "enraged", "angry", "mad", "infuriated",
    "this is stupid", "this is dumb", "pointless", "waste of time",
    "i'm done", "i give up", "over this",
    "ffs", "for fuck's sake", "i can't even", "i'm so done",

    # Dismissive, Sarcastic & Negative
    "whatever", "don't care", "who cares", "so what", "big deal",
    "boring", "dull", "uninteresting", "lame",
    "wrong", "incorrect", "false", "fake",
    "never", "always", "constantly", "literally", # Often used in hyperbole

    # Insulting concepts/things (not people)
    "this idea is idiotic", "your argument is stupid", "this code is garbage",
    "what a moronic statement", "that's a dumb idea", "your logic is flawed",

    # Passive-Aggressive & Escalatory Language
    "obviously", "clearly", "actually", "in fact",
    "you always", "you never", "you people", "seriously?", "really?",
    "if you say so", "sure, jan", "ok boomer", "bless your heart",
    "with all due respect", "no offense but", "just saying",

    # General Negativity
    "bad", "worst", "shame", "disgrace", "failure", "disaster",
    "ruined", "broken", "useless", "hopeless",
}


# --- Tricky words that can be non-toxic in some contexts ---
POSITIVE_CONTEXT_WORDS = {
    "the shit", "bad ass", "badass", "fucking awesome", "fucking great",
    "hell yeah", "damn good", "shit hot", "sick as fuck", "dope as fuck",
}

# --- Combined Hinglish Keywords for Language Detection ---
HINGLISH_KEYWORDS = {
    # Severe
    "madarchod", "bhenchod", "bhen ke lode", "bsdk", "bkl", "chutiye", "gandu",
    "teri maa ki", "teri maa ka", "randi", "gaandu", "mc", "bc", "mkl",
    # Cyberbullying
    "chutiya", "saala", "kutta", "kuttiya", "pagal", "bewakoof",
    "bakwaas band kar", "chup kar", "kamina", "harami", "nalayak", "gadha",
    "ullu ka pattha", "dimag kharab hai", "nikal", "chal nikal",
    # Toxic
    "bakwaas", "kya bakwaas hai", "abe", "hatt", "chal hatt", "kya musibat hai",
}


def _find_first_match(text: str, word_set: set) -> str | None:
    """Helper to find the first keyword from a set that exists in the text."""
    for word in word_set:
        if word in text:
            return word
    return None
    
def get_classification_from_keywords(text: str, context: str = None) -> dict:
    """
    Classifies text based on keyword matching.
    Follows a more nuanced hierarchy to improve accuracy.
    """
    lowered_text = text.lower().strip()
    lowered_context = context.lower().strip() if context else ""

    # --- New Contextual Logic: Check for "mirroring" insults ---
    MIRRORING_PHRASES = {
        "so are you", "you too", "right back at you", "just like you", 
        "takes one to know one", "no you",
        # Hinglish equivalents
        "tu bhi", "aap bhi", "tere jaisa", "tere jese",
    }
    # Check for exact phrases or phrases that imply "like you"
    is_mirroring = any(phrase in lowered_text for phrase in MIRRORING_PHRASES)

    if is_mirroring:
        if lowered_context:
            # If the context contained ANY form of toxicity, a mirroring reply escalates it to a personal attack.
            context_is_toxic = any(word in lowered_context for word in SEVERE_OVERLAP_WORDS) or \
                               any(word in lowered_context for word in CYBERBULLYING_WORDS) or \
                               any(word in lowered_context for word in TOXIC_WORDS)
            if context_is_toxic:
                return {
                    "label": "toxic",
                    "probability": 0.92, # High confidence as it's a direct retaliation
                    "cyberbullying_label": "cyberbullying",
                    "cyberbullying_score": 0.92,
                }

    # --- Step 1: Check for exact keyword matches (100% confidence) ---
    if lowered_text in SEVERE_OVERLAP_WORDS:
        return {"label": "toxic", "probability": 1.0, "cyberbullying_label": "cyberbullying", "cyberbullying_score": 1.0}
    if lowered_text in CYBERBULLYING_WORDS:
        return {"label": "toxic", "probability": 1.0, "cyberbullying_label": "cyberbullying", "cyberbullying_score": 1.0}
    if lowered_text in TOXIC_WORDS:
        return {"label": "toxic", "probability": 1.0, "cyberbullying_label": "not cyberbullying", "cyberbullying_score": 0.0}

    # --- Step 2: Check for positive contexts that override toxic words ---
    # If a "bad word" is used in a known positive phrase, classify as non-toxic immediately.
    if any(phrase in lowered_text for phrase in POSITIVE_CONTEXT_WORDS):
        return {"label": "non-toxic", "probability": 0.99, "cyberbullying_label": "not cyberbullying", "cyberbullying_score": 0.01}

    # --- Step 3: Check for keywords within a sentence (variable confidence) ---
    matched_severe = _find_first_match(lowered_text, SEVERE_OVERLAP_WORDS)
    matched_cyberbullying = _find_first_match(lowered_text, CYBERBULLYING_WORDS)
    matched_toxic = _find_first_match(lowered_text, TOXIC_WORDS)

    # --- Step 4: Apply logic based on flags ---
    # If severe words are present, it's the highest priority.
    if matched_severe:
        # Base score of 92%, with a more impactful bonus for longer phrases.
        score = min(0.99, 0.92 + len(matched_severe) * 0.004)
        return {
            "label": "toxic",
            "probability": score,
            "cyberbullying_label": "cyberbullying",
            "cyberbullying_score": score,
        }
    
    # If cyberbullying words are present (and no severe words), it's still toxic.
    if matched_cyberbullying:
        # Base score of 85%, creating a wider gap from severe.
        score = min(0.95, 0.85 + len(matched_cyberbullying) * 0.005)
        return {
            "label": "toxic", # Cyberbullying IS a form of toxicity.
            "probability": score,
            "cyberbullying_label": "cyberbullying",
            "cyberbullying_score": score,
        }

    # If only general toxic words are found.
    if matched_toxic:
        # Base score of 75%, with a strong bonus for length to show variance.
        score = min(0.90, 0.75 + len(matched_toxic) * 0.008)
        return {"label": "toxic", "probability": score, "cyberbullying_label": "not cyberbullying", "cyberbullying_score": 0.10}

    # If no keywords from any list are found, it's clean.
    return {"label": "non-toxic", "probability": 0.99, "cyberbullying_label": "not cyberbullying", "cyberbullying_score": 0.01}
