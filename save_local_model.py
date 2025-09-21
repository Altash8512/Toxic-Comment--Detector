# save_local_model.py

import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def main():
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toxic_model")
    os.makedirs(target_dir, exist_ok=True)

    model_id = "sarkararnab/toxic_bert_model"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)

    tokenizer.save_pretrained(target_dir)
    model.save_pretrained(target_dir)

    print(f"Saved model and tokenizer to: {target_dir}")


if __name__ == "__main__":
    main()


