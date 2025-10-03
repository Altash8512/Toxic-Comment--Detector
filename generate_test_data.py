import pandas as pd
import random
import uuid
from config import TOXIC_WORDS, CYBERBULLYING_WORDS, SEVERE_OVERLAP_WORDS

# --- Configuration ---
NUM_TRAIN_SAMPLES = 2000
NUM_TEST_SAMPLES = 1000

# --- Sentence Templates ---
NON_TOXIC_TEMPLATES = [
    "I really enjoyed this article, thanks for sharing.",
    "What a beautiful day outside!",
    "The new update looks promising, I'm excited to try it.",
    "Could you please explain that in more detail?",
    "I agree with your point about the economy.",
    "This is a very insightful comment.",
    "Thank you for your contribution to the discussion.",
    "I'm looking forward to the weekend.",
    "The cat is sleeping on the sofa.",
    "Let's try to keep the conversation civil.",
    "This movie was the shit! So good.", # Tricky: contains a keyword but is positive
    "He is a bad-ass character.", # Tricky: contains a keyword but is positive/neutral
    "That concert was fucking awesome!", # Tricky: profanity used for emphasis
    "What the hell, that's amazing!", # Tricky: profanity used for emphasis
]

SUBTLE_TOXIC_TEMPLATES = [
    "People like you are the reason this community is failing.", # Toxic without specific keywords
    "I'm not surprised you would think that.", # Condescending
    "Maybe you should educate yourself before commenting.", # Condescending
    "Your opinion is completely irrelevant here.", # Dismissive
    "Are you always this slow?", # Insulting without using a direct slur
    "I've seen better arguments from a child.", # Belittling
]

def generate_comment(category):
    """Generates a comment based on a category and keyword list."""
    if category == "non-toxic":
        return random.choice(NON_TOXIC_TEMPLATES)
    if category == "subtle-toxic":
        return random.choice(SUBTLE_TOXIC_TEMPLATES)
    
    word_list = []
    if category == "toxic":
        word_list = list(TOXIC_WORDS)
        template = "Your argument is {word} and makes no sense."
    elif category == "cyberbullying":
        word_list = list(CYBERBULLYING_WORDS)
        template = "You are such a {word}, nobody agrees with you."
    elif category == "severe":
        word_list = list(SEVERE_OVERLAP_WORDS)
        template = "I can't believe you said that, {word}."

    if not word_list:
        return ""
        
    keyword = random.choice(word_list)
    return template.format(word=keyword)

def create_dataset(num_samples):
    """Creates a dataset with a mix of comment types."""
    data = []
    categories = {
        "non-toxic": (0, 0, 0, 0),
        "subtle-toxic": (1, 0, 0, 0), # Labeled toxic, but keyword detector will miss it
        "toxic": (1, 0, 0, 0),
        "cyberbullying": (1, 0, 1, 0), # Cyberbullying is also toxic and an insult
        "severe": (1, 1, 1, 1), # Severe is toxic, severe_toxic, insult, and threat
    }

    for _ in range(num_samples):
        cat_name = random.choice(list(categories.keys()))
        comment_text = generate_comment(cat_name)
        
        # Handle tricky cases where a "non-toxic" template might have a keyword
        is_tricky_positive = any(p in comment_text.lower() for p in ["the shit", "bad-ass", "fucking awesome", "what the hell, that's amazing"])
        if is_tricky_positive:
            labels = categories["non-toxic"] # Override to be non-toxic
        else:
            labels = categories[cat_name]

        row = {
            "id": str(uuid.uuid4())[:16],
            "comment_text": comment_text,
            "toxic": labels[0],
            "severe_toxic": labels[1],
            "insult": labels[2],
            "threat": labels[3],
        }
        data.append(row)
    
    return pd.DataFrame(data)

def main():
    """Main function to generate and save all required CSV files."""
    print("Generating synthetic datasets...")

    # --- Generate train.csv ---
    # The rewriter evaluation script uses this file.
    print(f"  - Creating train.csv with {NUM_TRAIN_SAMPLES} samples...")
    train_df = create_dataset(NUM_TRAIN_SAMPLES)
    train_df.to_csv("train.csv", index=False)
    print("    ✅ Done.")

    # --- Generate test.csv and test_labels.csv ---
    # The main classification evaluation script uses these.
    print(f"  - Creating test.csv and test_labels.csv with {NUM_TEST_SAMPLES} samples...")
    test_df = create_dataset(NUM_TEST_SAMPLES)
    
    # Split into test.csv (text only) and test_labels.csv (labels only)
    test_comments_df = test_df[["id", "comment_text"]]
    test_labels_df = test_df[["id", "toxic", "severe_toxic", "insult", "threat"]]

    # Add some "-1" rows to simulate the real Kaggle dataset structure
    for _ in range(int(NUM_TEST_SAMPLES * 0.1)):
        test_labels_df.loc[random.choice(test_labels_df.index), "toxic":] = -1

    test_comments_df.to_csv("test.csv", index=False)
    test_labels_df.to_csv("test_labels.csv", index=False)
    print("    ✅ Done.")

    print("\n🎉 Successfully created train.csv, test.csv, and test_labels.csv!")
    print("You can now run 'python evaluate.py' and 'python evaluate_rewriter.py'.")

if __name__ == "__main__":
    main()