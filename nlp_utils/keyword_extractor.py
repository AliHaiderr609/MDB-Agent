from keybert import KeyBERT

# Global variable to hold the model instance (Singleton pattern)
_kw_model = None

def get_keyword_model():
    global _kw_model
    if _kw_model is None:
        print("Loading KeyBERT model (this may take a moment on first run)...")
        # We use a lightweight model for speed and efficiency
        _kw_model = KeyBERT(model='all-MiniLM-L6-v2')
    return _kw_model

def extract_keywords(text, top_n=5):
    """
    Extracts the most relevant keywords from a piece of text.
    """
    if not text or len(text.strip()) < 5:
        return []
        
    model = get_keyword_model()
    # extract_keywords returns a list of (keyword, score) tuples
    keywords_with_scores = model.extract_keywords(
        text, 
        keyphrase_ngram_range=(1, 2), 
        stop_words='english',
        top_n=top_n
    )
    
    # Return just the strings
    return [kw[0] for kw in keywords_with_scores]

if __name__ == "__main__":
    test_text = "Primary memory is frequently referred to as main memory. It is the memory that is directly accessible by the CPU."
    print(f"Text: {test_text}")
    print(f"Keywords: {extract_keywords(test_text)}")
