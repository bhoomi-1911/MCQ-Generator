import streamlit as st
import spacy
import random
from collections import Counter
import re
import PyPDF2
import io
from pdfminer.high_level import extract_text as pdfminer_extract_text

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(uploaded_file):
    try:
        # Try with pdfminer for better text extraction
        return pdfminer_extract_text(io.BytesIO(uploaded_file.read()))
    except:
        # Fallback to PyPDF2
        try:
            uploaded_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except:
            return ""

def extract_text_from_txt(uploaded_file):
    return str(uploaded_file.read(), "utf-8")

def generate_mcqs(text, num_questions=5):
    # Clean text more thoroughly
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    # Use spaCy for better sentence segmentation
    doc = nlp(clean_text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
    
    # If we don't have enough sentences, try manual splitting
    if len(sentences) < num_questions:
        sentences = [s.strip() for s in re.split(r'[.!?]', clean_text) if len(s.strip()) > 10]
    
    # Extract nouns from the entire text
    all_nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    noun_freq = Counter(all_nouns)
    common_nouns = [word for word, _ in noun_freq.most_common(30)]
    
    # If we still don't have enough sentences, create some from parts of text
    if len(sentences) < num_questions:
        # Split text into chunks and use them as sentences
        words = clean_text.split()
        chunk_size = max(10, len(words) // num_questions)
        sentences = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        sentences = [s for s in sentences if len(s) > 20][:num_questions]
    
    # Select sentences for questions
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))
    mcqs = []
    
    for sent in selected_sentences:
        doc_sent = nlp(sent)
        nouns_in_sent = [token.text for token in doc_sent if token.pos_ == "NOUN"]
        
        if nouns_in_sent:
            answer = random.choice(nouns_in_sent)
            # Create better distractors
            distractors = []
            for noun in common_nouns:
                if noun != answer and noun not in nouns_in_sent:
                    distractors.append(noun)
                if len(distractors) >= 3:
                    break
            
            # If we don't have enough distractors, create some
            while len(distractors) < 3:
                fake_noun = random.choice(["person", "thing", "place", "time", "way", "idea"])
                if fake_noun not in distractors and fake_noun != answer:
                    distractors.append(fake_noun)
            
            options = distractors + [answer]
            random.shuffle(options)
            question = sent.replace(answer, "______", 1)
            mcqs.append({"question": question, "options": options, "answer": answer})
    
    return mcqs

st.title("MCQ Generator")

# Initialize session state variables
if "mcqs" not in st.session_state:
    st.session_state.mcqs = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "text_input" not in st.session_state:
    st.session_state.text_input = ""

# Input options - text area or file upload
input_method = st.radio("Choose input method:", ("Text Input", "File Upload"))

if input_method == "Text Input":
    st.session_state.text_input = st.text_area("Paste your text here:", value=st.session_state.text_input)
else:
    uploaded_file = st.file_uploader("Upload a PDF or text file", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.session_state.text_input = extract_text_from_pdf(uploaded_file)
            st.info(f"Extracted {len(st.session_state.text_input)} characters from PDF")
        elif uploaded_file.type == "text/plain":
            st.session_state.text_input = extract_text_from_txt(uploaded_file)
            st.info(f"Extracted {len(st.session_state.text_input)} characters from text file")

num_questions = st.number_input("Number of MCQs:", min_value=1, max_value=20, value=5)

# Display extracted text for debugging
if st.session_state.text_input and st.checkbox("Show extracted text"):
    st.text_area("Extracted Text", st.session_state.text_input, height=200)

# Generate MCQs
if st.button("Generate MCQs") and st.session_state.text_input:
    with st.spinner("Generating questions..."):
        st.session_state.mcqs = generate_mcqs(st.session_state.text_input, num_questions)
        st.session_state.user_answers = [""] * len(st.session_state.mcqs)
        st.session_state.submitted = False
        st.rerun()

# Display MCQs and calculate score
if st.session_state.mcqs:
    # Calculate score if submitted
    score = 0
    if st.session_state.submitted:
        for i, q in enumerate(st.session_state.mcqs):
            if st.session_state.user_answers[i] == q['answer']:
                score += 1
    
    # Display score if submitted
    if st.session_state.submitted:
        st.subheader(f"Score: {score}/{len(st.session_state.mcqs)}")
    
    # Create a form to wrap all questions
    with st.form(key="mcq_form"):
        for i, q in enumerate(st.session_state.mcqs):
            st.write(f"Q{i+1}: {q['question']}")
            
            # Use a unique key for each radio button
            user_answer = st.radio(
                f"Select answer for Q{i+1}:",
                q['options'],
                key=f"option_{i}"
            )
            st.session_state.user_answers[i] = user_answer
            
            # Show feedback inline if submitted
            if st.session_state.submitted:
                if st.session_state.user_answers[i] == q['answer']:
                    st.success("✅ Correct")
                else:
                    st.error(f"❌ Wrong (Correct: {q['answer']})")
            st.write("---")
        
        # Submit button inside the form
        submitted = st.form_submit_button("Submit Answers")
        if submitted:
            st.session_state.submitted = True
            st.rerun()
