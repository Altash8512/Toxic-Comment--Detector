# predict.py

import os

# Avoid optional image deps (torchvision) being imported by transformers
os.environ.setdefault("TRANSFORMERS_NO_TORCHVISION", "1")
os.environ.setdefault("TRANSFORMERS_NO_PYTORCH_IMAGE", "1")
os.environ.setdefault("FORCE_TORCHVISION_AVAILABLE", "0")
os.environ.setdefault("FORCE_TORCHAUDIO_AVAILABLE", "0")
os.environ.setdefault("FORCE_TENSORFLOW_AVAILABLE", "0")
os.environ.setdefault("FORCE_FLAX_AVAILABLE", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# --- Device Configuration ---
# Use GPU if available, otherwise fall back to CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✅ Device set to use: {str(DEVICE).upper()}")

def _resolve_model_source() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_model_dir = os.path.join(current_dir, "toxic_model")

    expected_files = [
        os.path.join(local_model_dir, "config.json"),
        os.path.join(local_model_dir, "tokenizer_config.json"),
    ]
    if os.path.isdir(local_model_dir) and all(os.path.exists(p) for p in expected_files):
        return local_model_dir

    return "sarkararnab/toxic_bert_model"


MODEL_SOURCE = _resolve_model_source()

tokenizer = AutoTokenizer.from_pretrained(MODEL_SOURCE)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_SOURCE)
model.to(DEVICE)
model.eval()

labels = ['non-toxic', 'toxic']

def _resolve_cyber_model_source() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_dir = os.path.join(current_dir, "cyber_model")
    if os.path.isdir(local_dir) and os.path.exists(os.path.join(local_dir, "config.json")):
        return local_dir
    # Smaller MNLI model for zero-shot to keep size reasonable
    return "typeform/distilbert-base-uncased-mnli"


CYBER_MODEL_SOURCE = _resolve_cyber_model_source()

# Try to load zero-shot pipeline lazily, but gracefully degrade if not available
_zero_shot = None
try:
    from transformers import pipeline as _hf_pipeline
    _zero_shot = _hf_pipeline(
        task="zero-shot-classification",
        model=CYBER_MODEL_SOURCE,
        tokenizer=CYBER_MODEL_SOURCE,
        device=0 if DEVICE.type == "cuda" else -1,  # Use 0 for GPU, -1 for CPU
    )
except Exception:
    _zero_shot = None

CYBER_LABELS = [
    "cyberbullying",
    "harassment",
    "threat",
    "insult",
    "not cyberbullying",
]

def _classify_cyberbullying(text: str):
    if _zero_shot is None:
        # Let the Flask app's heuristic augmentation fill these if needed
        return "not cyberbullying", 0.0
    result = _zero_shot(
        text,
        candidate_labels=CYBER_LABELS,
        multi_label=True,
    )
    # Map to a simple label/score
    scores = {label.lower(): score for label, score in zip(result["labels"], result["scores"])}
    bullying_score = max(
        scores.get("cyberbullying", 0.0),
        scores.get("harassment", 0.0),
        scores.get("threat", 0.0),
        scores.get("insult", 0.0),
    )
    label = "cyberbullying" if bullying_score >= 0.5 else "not cyberbullying"
    return label, float(round(bullying_score, 4))

def predict_comment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        pred_label = torch.argmax(probs, dim=1).item()
    cyber_label, cyber_score = _classify_cyberbullying(text)
    out = {
        "label": labels[pred_label],
        "probability": round(probs[0][pred_label].item(), 4),
        "cyberbullying_label": cyber_label,
        "cyberbullying_score": cyber_score,
    }
    return out
