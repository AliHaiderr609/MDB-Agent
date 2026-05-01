import os
import sys

# Ensure we can import from nlp_utils
sys.path.append(os.path.dirname(__file__))

from nlp_utils.pdf_processor import extract_text_from_pdf
from nlp_utils.academic_filter import is_academic_query
from nlp_utils.keyword_extractor import extract_keywords
from nlp_utils.semantic_search import get_best_match, chunk_text

def run_tests():
    print("=== Phase 2: NLP Utility Verification ===\n")
    
    # 1. Test Filter
    print("1. Testing Academic Filter...")
    queries = ["What is RAM?", "present sir", "ok done"]
    for q in queries:
        is_acad, reason = is_academic_query(q)
        print(f"  - '{q}': {'PASS' if is_acad else 'BLOCKED (' + reason + ')'}")
    
    # 2. Test PDF Extraction
    print("\n2. Testing PDF Processor...")
    pdf_path = os.path.join(os.path.dirname(__file__), "user manual.pdf")
    if os.path.exists(pdf_path):
        text = extract_text_from_pdf(pdf_path)
        print(f"  - Successfully extracted {len(text)} characters from User Manual.")
    else:
        text = "This is a sample text about computer architecture and primary memory systems."
        print("  - User manual not found, using fallback text.")

    # 3. Test Keyword Extraction
    print("\n3. Testing Keyword Extractor (Loading Model)...")
    sample_text = "Primary memory is frequently referred to as main memory. It is the memory that is directly accessible by the CPU."
    keywords = extract_keywords(sample_text)
    print(f"  - Text: {sample_text}")
    print(f"  - Keywords: {keywords}")

    # 4. Test Semantic Search
    print("\n4. Testing Semantic Search (Loading Model)...")
    chunks = [
        "Primary memory is directly accessible by the CPU.",
        "Secondary memory is used for long-term storage.",
        "The ALU performs arithmetic and logic operations.",
        "A PDF file format is used for sharing documents."
    ]
    query = "Where is the CPU's main memory?"
    match, score = get_best_match(query, chunks)
    print(f"  - Query: {query}")
    print(f"  - Best Match: '{match}' (Confidence: {score:.4f})")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    run_tests()
