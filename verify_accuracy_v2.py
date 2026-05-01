import os
import sys

# Corrected Path
sys.path.append(os.getcwd())

from nlp_utils.pdf_processor import extract_text_from_pdf
from nlp_utils.semantic_search import chunk_text, get_best_match

def verify_accuracy():
    print("Verifying Accuracy Fixes...")
    
    # 1. Test Handout Preparation
    handout_text = """
To register as a student:
1. Open the Registration page.
2. Enter your Name, Email, and Password.
3. Click the Register button.
4. Log in to access the AI Agent.

After installing python and Flask just run start app file.
The system features include user registration, login, and an AI chat interface.
    """
    
    chunks = chunk_text(handout_text)
    print(f"Total Chunks: {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"Chunk {i}: {c[:100]}...")

    # 2. Test "What is CPU?" (HALLUCINATION CHECK)
    query1 = "What is CPU?"
    best_chunk1, score1 = get_best_match(query1, chunks)
    print(f"\nQuery: '{query1}'")
    print(f"Best Score: {score1:.4f} (Threshold: 0.35)")
    if score1 < 0.35:
        print("✅ SUCCESS: AI correctly refused to answer (Fallback).")
    else:
        print(f"❌ FAILURE: AI matched to: {best_chunk1}")

    # 3. Test "How to register as student?" (CUTOFF CHECK)
    query2 = "How to register as student?"
    best_chunk2, score2 = get_best_match(query2, chunks)
    print(f"\nQuery: '{query2}'")
    print(f"Best Score: {score2:.4f}")
    if "Click the Register button" in best_chunk2:
        print("✅ SUCCESS: Full steps retrieved (No Cutoff).")
    else:
        print(f"❌ FAILURE: Response is incomplete: {best_chunk2}")

if __name__ == "__main__":
    verify_accuracy()
