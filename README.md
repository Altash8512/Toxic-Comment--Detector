<div align="center">
  <h1>🛡️ Toxic Comment Detector & Recommender</h1>
  <p>
    An intelligent system powered by the Google Gemini API that detects toxic, cyberbullying, and Hinglish comments in real-time and suggests polite alternatives.
  </p>
</div>

---

## 🌟 Key Features
*   **Real-Time Detection**: Uses a fast, local keyword-based classifier for instant feedback on toxic, cyberbullying, and Hinglish language.
*   **Contextual Understanding**: Intelligently assesses if a reply is toxic based on the parent comment it's responding to.
*   **AI-Powered Rewrites**: Leverages the Google Gemini API to provide high-quality, polite alternative phrasings for toxic comments.
*   **Hinglish Support**: Natively understands and processes Hinglish (Hindi + English) for both detection and rewriting.

## 🖼️ Screenshots

<div align="center">
  <img src="screenshots/out.png" width="48%" alt="Web App Screenshot 1">
  <img src="screenshots/out2.png" width="48%" alt="Web App Screenshot 2">
  <p><i>Main application interface for toxicity analysis and recommendations.</i></p>
</div>

---

## 🛠️ Technology Stack

| Layer             | Technology                                   |
|:------------------|:---------------------------------------------|
| **Web Backend**   | Flask (Python)                               |
| **AI Service**    | Google Gemini API                            |
| **Frontend**      | HTML, Tailwind CSS, JavaScript               |

---

## 📊 Keyword Detector Performance

The performance of the local keyword-based classifier was evaluated on a synthetically generated test set of 1,000 comments, mimicking the structure of the Jigsaw Toxic Comment Classification dataset.

> **To generate these results yourself:**
> 1.  Run `python generate_test_data.py` to create the test files.
> 2.  Run `python evaluate_keyword_model.py` to print the reports and save the matrices.

### 1. Toxicity Detection

<img src="screenshots/toxicity_confusion_matrix.png" width="400" alt="Toxicity Confusion Matrix">

```
              precision    recall  f1-score   support

   Not Toxic       0.96      0.98      0.97       815
       Toxic       0.89      0.82      0.85       185

    accuracy                           0.95      1000
   macro avg       0.92      0.90      0.91      1000
weighted avg       0.95      0.95      0.95      1000
```

### 2. Cyberbullying Detection

<img src="screenshots/cyberbullying_confusion_matrix.png" width="400" alt="Cyberbullying Confusion Matrix">

```
                   precision    recall  f1-score   support

Not Cyberbullying       0.98      0.99      0.98       808
    Cyberbullying       0.93      0.88      0.90       192

         accuracy                           0.97      1000
        macro avg       0.95      0.93      0.f94      1000
     weighted avg       0.97      0.97      0.97      1000
```

---

## ⚙️ Local Setup and Installation

Follow these steps to run the project locally.

### 1. Prerequisites
- Python 3.10 or newer

### 2. Clone the Repository
```bash
git clone https://github.com/altamashchougle/Toxic-Comment--Detector.git
cd Toxic-Comment--Detector
```

### 3. Set Up Virtual Environment
```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables 
+Create a .env file in the root directory of the project and add your Google Gemini API key. This is required for the AI-powered rewrite suggestions.

### 6. Run the Application
```bash
python app.py
```
The server will be available at `http://127.0.0.1:10000`.

---
