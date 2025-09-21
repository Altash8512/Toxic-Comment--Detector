import os
import subprocess
from typing import Tuple

import pandas as pd
from datasets import Dataset, load_dataset
from transformers import (
    T5ForConditionalGeneration,
    T5TokenizerFast,
    Trainer,
    TrainingArguments,
)
import torch


def _load_and_prepare_dataset(max_rows: int = 20000) -> Dataset:
    """
    Loads the Anthropic HH-RLHF dataset to train a detoxification model.
    This dataset contains pairs of "chosen" (less harmful) and "rejected" (more harmful)
    responses, which is ideal for teaching a model to rephrase text.
    """
    print("Loading Anthropic Harmlessness dataset...")
    # We use the 'harmless-base' subset for detoxification training
    ds = load_dataset("Anthropic/hh-rlhf", data_dir="harmless-base", split="train")
    df = ds.to_pandas()
    
    # The 'rejected' column contains the more toxic text (our input)
    # The 'chosen' column contains the less toxic, preferred text (our target)
    df = df.rename(columns={"rejected": "input_text_raw", "chosen": "target_text_raw"})
    df = df[["input_text_raw", "target_text_raw"]].dropna()
    df = df.sample(n=min(max_rows, len(df)), random_state=42)
    
    inputs, targets = [], []
    for rejected, chosen in zip(df["input_text_raw"].tolist(), df["target_text_raw"].tolist()):
        inputs.append(f"detoxify: {rejected.strip()}")
        targets.append(chosen.strip())
        
    dataset = Dataset.from_dict({"input_text": inputs, "target_text": targets})
    return dataset


def train_t5_rewriter(output_dir: str = "rewriter_model", base_model: str = "t5-small", max_steps: int = 1000):
    dataset = _load_and_prepare_dataset()
    
    tokenizer = T5TokenizerFast.from_pretrained(base_model)
    model = T5ForConditionalGeneration.from_pretrained(base_model)

    def preprocess(batch):
        model_inputs = tokenizer(batch["input_text"], truncation=True, padding="max_length", max_length=128)
        labels = tokenizer(batch["target_text"], truncation=True, padding="max_length", max_length=64)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = dataset.map(preprocess, batched=True, remove_columns=["input_text", "target_text"])

    args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=3e-4,
        per_device_train_batch_size=16,
        num_train_epochs=1,
        max_steps=max_steps,
        logging_steps=50,
        save_steps=500,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        tokenizer=tokenizer,
    )

    trainer.train()
    os.makedirs(output_dir, exist_ok=True)
    tokenizer.save_pretrained(output_dir)
    model.save_pretrained(output_dir)
    print(f"Rewriter model saved to {output_dir}")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "rewriter_model")
    train_t5_rewriter(output_dir=out)
