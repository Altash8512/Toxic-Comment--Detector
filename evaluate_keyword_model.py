import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from config import get_classification_from_keywords

def evaluate_model():
    """
    Evaluates the keyword-based classification model using the generated test set.
    """
    print("📊 Starting evaluation of the keyword-based model...")

    try:
        comments_df = pd.read_csv("test.csv")
        labels_df = pd.read_csv("test_labels.csv")
    except FileNotFoundError:
        print("❌ Error: 'test.csv' or 'test_labels.csv' not found.")
        print("Please run 'python generate_test_data.py' first to create the test files.")
        return

    # Merge comments and labels, and drop rows with -1 (unlabeled in Kaggle format)
    df = pd.merge(comments_df, labels_df, on="id")
    df = df[df["toxic"] != -1].copy()

    # Get predictions from our keyword-based function
    predictions = df["comment_text"].apply(get_classification_from_keywords)
    df["predicted_toxic"] = [p.get("label") == "toxic" for p in predictions]
    df["predicted_cyberbullying"] = [p.get("cyberbullying_label") == "cyberbullying" for p in predictions]

    # --- Evaluate Toxicity Detection ---
    print("\n" + "="*30)
    print("  TOXICITY DETECTION REPORT")
    print("="*30)
    y_true_toxic = df["toxic"].astype(int)
    y_pred_toxic = df["predicted_toxic"].astype(int)
    print(classification_report(y_true_toxic, y_pred_toxic, target_names=["Not Toxic", "Toxic"]))
    print(f"Toxicity Detection Accuracy: {accuracy_score(y_true_toxic, y_pred_toxic):.2%}")

    # Plot and save confusion matrix for toxicity
    cm_toxic = confusion_matrix(y_true_toxic, y_pred_toxic)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_toxic, annot=True, fmt="d", cmap="Blues", xticklabels=["Not Toxic", "Toxic"], yticklabels=["Not Toxic", "Toxic"])
    plt.title("Toxicity Confusion Matrix")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.savefig("screenshots/toxicity_confusion_matrix.png")
    print("✅ Saved 'toxicity_confusion_matrix.png'")

    # --- Evaluate Cyberbullying Detection ---
    print("\n" + "="*30)
    print("  CYBERBULLYING DETECTION REPORT")
    print("="*30)
    y_true_cyber = (df["insult"] == 1) | (df["threat"] == 1)
    y_pred_cyber = df["predicted_cyberbullying"].astype(int)
    print(classification_report(y_true_cyber, y_pred_cyber, target_names=["Not Cyberbullying", "Cyberbullying"]))
    print(f"Cyberbullying Detection Accuracy: {accuracy_score(y_true_cyber, y_pred_cyber):.2%}")

    cm_cyber = confusion_matrix(y_true_cyber, y_pred_cyber)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_cyber, annot=True, fmt="d", cmap="Oranges", xticklabels=["Not Cyberbullying", "Cyberbullying"], yticklabels=["Not Cyberbullying", "Cyberbullying"])
    plt.title("Cyberbullying Confusion Matrix")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.savefig("screenshots/cyberbullying_confusion_matrix.png")
    print("✅ Saved 'cyberbullying_confusion_matrix.png'")

if __name__ == "__main__":
    evaluate_model()