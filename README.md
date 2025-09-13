MCQ Generator

A Streamlit application that generates multiple-choice questions (MCQs) from text or PDF input. Users can either paste text directly or upload a file, specify the number of questions, and generate MCQs automatically. Each question includes multiple options, and users can select answers to receive immediate feedback and see their score.

Features

Supports text input and PDF/text file upload.

Automatically generates MCQs using NLP (spaCy).

Provides instant feedback for selected answers.

Displays score after submission.

Easy to use for practice quizzes and learning.

Installation

Clone the repository:
git clone <repo-url>
cd mcq-generator

Create a virtual environment and activate it:
python -m venv venv

macOS/Linux

source venv/bin/activate

Windows

venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt
python -m spacy download en_core_web_sm

Usage

Run the Streamlit app:
streamlit run mcq_generator.py

Select input method (Text Input or File Upload).

Paste your text or upload a PDF/text file.

Choose the number of MCQs.

Click "Generate MCQs".

Select answers and click "Submit Answers" to see feedback and score.
