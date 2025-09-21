import os
from typing import Optional

import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast

# --- Device Configuration ---
# Use GPU if available, otherwise fall back to CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


_REWRITER_DIR = os.path.join(os.path.dirname(__file__), "rewriter_model")

_tokenizer = None
_model = None


def load_rewriter_if_available() -> bool:
    global _tokenizer, _model
    if _model is not None and _tokenizer is not None:
        return True
    if not (os.path.isdir(_REWRITER_DIR) and os.path.exists(os.path.join(_REWRITER_DIR, "config.json"))):
        return False
    try:
        _tokenizer = T5TokenizerFast.from_pretrained(_REWRITER_DIR)
        _model = T5ForConditionalGeneration.from_pretrained(_REWRITER_DIR)
        _model.to(DEVICE)
        _model.eval()
        return True
    except Exception:
        _tokenizer = None
        _model = None
        return False


def generate_polite_rewrite(text: str, max_length: int = 64) -> Optional[str]:
    if _model is None or _tokenizer is None:
        if not load_rewriter_if_available():
            return None
    prompt = f"detoxify: {text.strip()}"
    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True).to(DEVICE)
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True,
            no_repeat_ngram_size=3,
        )
    decoded = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return decoded or None
