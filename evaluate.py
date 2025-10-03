import pandas as pd
from config import get_classification_from_keywords  # Use keyword-based logic
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
from tqdm import tqdm

def evaluate_model(text_column, sample_size=10000):
    """
    Evaluates the model on a given test dataset.

    Args:
        text_column (str): The name of the column containing the comment text.
        sample_size (int, optional): The number of rows to sample from the test set for evaluation.
                                     If None, the entire dataset is used. Defaults to 5000.
    """
    print("Loading and preparing test data...")
    try:
        # Load the comments and their corresponding labels
        df_test = pd.read_csv("test.csv")
        df_labels = pd.read_csv("test_labels.csv")

        # Combine them based on the 'id' column
        df = pd.merge(df_test, df_labels, on="id")

        # In test_labels.csv, -1 means the comment was not used for scoring.
        # We'll filter these out. We only want to evaluate on rows with a 0 or 1 label.
        # We check the 'toxic' column as a reference for this filtering.
        df = df[df['toxic'] != -1]
        
        if sample_size is not None and sample_size < len(df):
            print(f"  - Sampling {sample_size} rows from the dataset for evaluation.")
            df = df.sample(n=sample_size, random_state=42)
        else:
            print("  - Using the full dataset for evaluation.")

        print(f"  - Loaded and merged test.csv and test_labels.csv")

    except FileNotFoundError as e:
        print(f"❌ Error: Could not find the required test file: {e.filename}")
        print("Please make sure 'test.csv' and 'test_labels.csv' are in the same folder as this script.")
        return
    print(f"Total rows to evaluate: {len(df)}")

    # Define all the labels we will be using for evaluation
    label_columns = ['toxic', 'severe_toxic', 'insult', 'threat']
    required_cols = {text_column, *label_columns}
    if not required_cols.issubset(df.columns):
        print(f"❌ Error: The CSV must contain the following columns: {', '.join(required_cols)}")
        return

    # --- Prepare Ground Truth Labels ---
    # 1. Combined "Toxic" label: A comment is toxic if 'toxic' OR 'severe_toxic' is 1.
    df['true_any_toxic_id'] = df[['toxic', 'severe_toxic']].max(axis=1)

    # 2. Combined "Cyberbullying" label: A comment is cyberbullying if 'insult' OR 'threat' is 1.
    df['true_cyberbullying_id'] = df[['insult', 'threat']].max(axis=1)
    
    # --- Lists to store results ---
    true_toxic_labels = []
    pred_toxic_labels = []
    true_cyberbullying_labels = []
    pred_cyberbullying_labels = []

    print("Running predictions on the test set...")
    # Using tqdm for a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Predicting"):
        text = row[text_column]
        
        prediction_result = get_classification_from_keywords(text)
        
        # --- Process Toxic Prediction ---
        pred_toxic_str = prediction_result.get("label", "non-toxic")
        pred_any_toxic_id = 1 if pred_toxic_str.lower() == 'toxic' else 0
        true_toxic_labels.append(row['true_any_toxic_id'])
        pred_toxic_labels.append(pred_any_toxic_id)

        # --- Process Cyberbullying Prediction (Zero-Shot Model) ---
        pred_cyber_str = prediction_result.get("cyberbullying_label", "not cyberbullying")
        pred_cyber_id = 1 if pred_cyber_str.lower() == 'cyberbullying' else 0
        true_cyberbullying_labels.append(row['true_cyberbullying_id'])
        pred_cyberbullying_labels.append(pred_cyber_id)

    # --- Metrics for TOXIC classification ---
    print("\n" + "="*50)
    print("      EVALUATION FOR: General Toxicity (toxic OR severe_toxic)")
    print("="*50)
    accuracy = accuracy_score(true_toxic_labels, pred_toxic_labels)
    print(f"\n✅ 'Toxic' Model Accuracy: {accuracy:.4f}")

    print("\n'Toxic' Classification Report:")
    report = classification_report(true_toxic_labels, pred_toxic_labels, target_names=["Not Toxic", "Toxic"], zero_division=0)
    print(report)

    print("Generating 'Toxic' confusion matrix...")
    cm = confusion_matrix(true_toxic_labels, pred_toxic_labels, labels=[0, 1])
    display_labels = ["Not Toxic", "Toxic"]
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_labels)
    disp.plot(cmap=plt.cm.Blues)
    plt.title("Confusion Matrix for 'Toxic' Classification")
    plt.show(block=False) # Keep this non-blocking to show both plots

    # --- Metrics for CYBERBULLYING classification ---
    print("\n" + "="*50)
    print("    EVALUATION FOR: Cyberbullying (insult OR threat)")
    print("="*50)
    accuracy_cb = accuracy_score(true_cyberbullying_labels, pred_cyberbullying_labels)
    print(f"\n✅ 'Cyberbullying' Model Accuracy: {accuracy_cb:.4f}")

    print("\n'Cyberbullying' Classification Report:")
    report_cb = classification_report(true_cyberbullying_labels, pred_cyberbullying_labels, target_names=["Not Cyberbullying", "Cyberbullying"], zero_division=0)
    print(report_cb)

    print("Generating 'Cyberbullying' confusion matrix...")
    cm_cb = confusion_matrix(true_cyberbullying_labels, pred_cyberbullying_labels, labels=[0, 1])
    display_labels_cb = ["Not Cyberbullying", "Cyberbullying"]
    disp_cb = ConfusionMatrixDisplay(confusion_matrix=cm_cb, display_labels=display_labels_cb)
    disp_cb.plot(cmap=plt.cm.Oranges)
    plt.title("Confusion Matrix for 'Cyberbullying' Classification") # The final plot will block
    plt.show()

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # This script is now set up to use 'test.csv' and 'test_labels.csv'
    # from the Kaggle Toxic Comment Classification Challenge by default.
    
    SAMPLE_SIZE = 10000                 # <--- Set to None to evaluate the full dataset
    TEXT_COLUMN = "comment_text"
    
    evaluate_model(TEXT_COLUMN, sample_size=SAMPLE_SIZE)