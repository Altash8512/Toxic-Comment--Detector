import os
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def main():
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_model")
    os.makedirs(target_dir, exist_ok=True)

    model_id = "typeform/distilbert-base-uncased-mnli"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_id)

    tok.save_pretrained(target_dir)
    mdl.save_pretrained(target_dir)
    print(f"Saved cyberbullying zero-shot model to: {target_dir}")


if __name__ == "__main__":
    main()


