import pandas as pd
from tqdm import tqdm
from rewriter import generate_polite_rewrite
# from gemini_suggester import suggest_with_gemini  # Temporarily disabled for T5-only evaluation
from predict import predict_comment
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score
import matplotlib.pyplot as plt

def evaluate_rewriters(sample_size=1000, toxicity_threshold=0.5):
    """
    Generates a qualitative evaluation sheet for the rewriter models.

    It samples toxic comments, runs them through the T5 and Gemini rewriters,
    and saves the output to a CSV for manual review.

    Args:
        sample_size (int): The number of toxic comments to sample for evaluation.
        toxicity_threshold (float): The minimum toxicity score to be considered 'toxic'.
                                    The Kaggle dataset uses this in the 'target' column.
    """
    output_file = "rewriter_evaluation_results.csv"
    print("Loading and preparing data for rewriter evaluation...")

    try:
        # We use the training data here as it has a continuous 'target' score
        # which is good for finding clearly toxic comments.
        df = pd.read_csv("train.csv")
        
        # Filter for comments that are considered toxic
        toxic_df = df[df['toxic'] >= toxicity_threshold]

        if len(toxic_df) < sample_size:
            print(f"⚠️ Warning: Found only {len(toxic_df)} toxic comments, less than sample size of {sample_size}.")
            sample_df = toxic_df
        else:
            sample_df = toxic_df.sample(n=sample_size, random_state=42)

        print(f"  - Sampled {len(sample_df)} toxic comments for evaluation.")

    except FileNotFoundError:
        print("❌ Error: Could not find 'train.csv'.")
        print("Please download 'train.csv' from the Kaggle competition to evaluate the rewriter.")
        return

    # --- Quantitative Evaluation ---
    # We expect a "successful" rewrite to be classified as "non-toxic".
    # Ground Truth: All rewrites should ideally be non-toxic (label 0).
    # We will check if our detector agrees.
    true_labels = [0] * len(sample_df) # 0 = non-toxic
    t5_predicted_labels = []
    # gemini_predicted_labels = [] # Temporarily disabled

    # --- Qualitative Evaluation ---
    results = []
    print("Generating rewrites for sampled comments...")
    for index, row in tqdm(sample_df.iterrows(), total=sample_df.shape[0], desc="Rewriting"):
        original_text = row['comment_text']
        
        # --- T5 Rewriter ---
        t5_rewrite = generate_polite_rewrite(original_text) or ""
        t5_result = predict_comment(t5_rewrite) if t5_rewrite else {"label": "toxic"}
        t5_pred_id = 0 if t5_result.get("label", "toxic").lower() == 'non-toxic' else 1
        t5_predicted_labels.append(t5_pred_id)
        
        # # --- Gemini Rewriter (Temporarily Disabled) ---
        # gemini_result = suggest_with_gemini(original_text)
        # gemini_rewrite = gemini_result.get("gemini_rewrite", "")
        # gemini_pred_result = predict_comment(gemini_rewrite) if gemini_rewrite else {"label": "toxic"}
        # gemini_pred_id = 0 if gemini_pred_result.get("label", "toxic").lower() == 'non-toxic' else 1
        # gemini_predicted_labels.append(gemini_pred_id)
        
        results.append({
            "original_comment": original_text,
            "t5_rewrite": t5_rewrite,
            # "gemini_rewrite": gemini_rewrite,
            "t5_rewrite_is_toxic": "Yes" if t5_pred_id == 1 else "No",
            # "gemini_rewrite_is_toxic": "Yes" if gemini_pred_id == 1 else "No",
        })

    # --- Save Qualitative Results to CSV ---
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Successfully generated qualitative results sheet.")
    print(f"Please review the results in '{output_file}'")

    # --- Display Quantitative Metrics for T5 Rewriter ---
    print("\n" + "="*50)
    print("      EVALUATION FOR: T5 Rewriter Model")
    print("="*50)
    accuracy = accuracy_score(true_labels, t5_predicted_labels)
    print(f"\n✅ Rewrite Success Rate (Accuracy): {accuracy:.4f}")

    print("\nClassification Report (Success = 'Non-Toxic'):")
    report_t5 = classification_report(true_labels, t5_predicted_labels, target_names=["Non-Toxic (Success)", "Toxic (Failure)"], zero_division=0)
    print(report_t5)

    print("Generating T5 Rewriter confusion matrix...")
    cm_t5 = confusion_matrix(true_labels, t5_predicted_labels, labels=[0, 1])
    disp_t5 = ConfusionMatrixDisplay(confusion_matrix=cm_t5, display_labels=["Non-Toxic (Success)", "Toxic (Failure)"])
    disp_t5.plot(cmap=plt.cm.Greens)
    plt.title("T5 Rewriter Performance (Post-Rewrite Analysis)")
    plt.show() # Changed to block=True (default) to keep the window open

    # # --- Display Quantitative Metrics for Gemini Rewriter (Temporarily Disabled) ---
    # print("\n" + "="*50)
    # print("      EVALUATION FOR: Gemini Rewriter Model")
    # print("="*50)
    # print("\nClassification Report (Success = 'Non-Toxic'):")
    # report_gemini = classification_report(true_labels, gemini_predicted_labels, target_names=["Non-Toxic (Success)", "Toxic (Failure)"], zero_division=0)
    # print(report_gemini)

    # print("Generating Gemini Rewriter confusion matrix...")
    # cm_gemini = confusion_matrix(true_labels, gemini_predicted_labels, labels=[0, 1])
    # disp_gemini = ConfusionMatrixDisplay(confusion_matrix=cm_gemini, display_labels=["Non-Toxic (Success)", "Toxic (Failure)"])
    # disp_gemini.plot(cmap=plt.cm.Purples)
    # plt.title("Gemini Rewriter Performance (Post-Rewrite Analysis)")
    # plt.show()


if __name__ == "__main__":
    # Increased sample size for more meaningful metrics, but still fast.
    evaluate_rewriters(sample_size=1000)