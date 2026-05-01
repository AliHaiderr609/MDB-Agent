from sentence_transformers import SentenceTransformer, util
import numpy as np
import re

# Global variable to hold the model instance
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("Loading Sentence-Transformers model...")
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embed_model

def get_best_match(query, text_chunks):
    """
    Finds the most relevant text chunk based on the user query.
    Returns (best_chunk, score)
    """
    if not text_chunks:
        return None, 0.0
        
    model = get_embed_model()
    
    # Compute embeddings
    query_embedding = model.encode(query, convert_to_tensor=True)
    chunk_embeddings = model.encode(text_chunks, convert_to_tensor=True)
    
    # Compute cosine similarity
    scores = util.cos_sim(query_embedding, chunk_embeddings)[0]
    
    # Find the index of the highest score
    best_idx = np.argmax(scores.cpu().detach().numpy())
    best_score = float(scores[best_idx])
    
    return text_chunks[best_idx], best_score

def chunk_text(text, max_chars=1200, min_chars=30):
    """
    Splits text into structural 'Sticky' chunks.
    Prioritizes double newlines (\n\n) to keep headers and steps together.
    Normalizes internal whitespace within chunks.
    """
    if not text:
        return []
        
    # Step 1: Split by double newlines (logical blocks)
    blocks = [b.strip() for b in text.split('\n\n') if len(b.strip()) > 0]
    
    final_chunks = []
    for b in blocks:
        # Step 2: Normalize block (remove extra newlines/spaces)
        normalized_block = re.sub(r'\s+', ' ', b).strip()
        
        if len(normalized_block) <= max_chars:
            if len(normalized_block) >= min_chars:
                final_chunks.append(normalized_block)
        else:
            # Step 3: Sentence splitting only for extremely long blocks
            sentences = re.split(r'(?<=[.!?]) +', normalized_block)
            current_chunk = ""
            for s in sentences:
                if len(current_chunk) + len(s) < max_chars:
                    current_chunk += (" " + s if current_chunk else s)
                else:
                    if len(current_chunk) >= min_chars:
                        final_chunks.append(current_chunk.strip())
                    current_chunk = s
            if current_chunk and len(current_chunk) >= min_chars:
                final_chunks.append(current_chunk.strip())
                
    return final_chunks

if __name__ == "__main__":
    sample_chunks = [
        "Primary memory is the main memory of the computer. It is volatile.",
        "Secondary memory like Hard Disks is used for permanent storage.",
        "The CPU executes instructions by fetching them from RAM.",
        "Printers and Keyboards are input/output devices."
    ]
    
    test_query = "What is the main memory?"
    match, score = get_best_match(test_query, sample_chunks)
    print(f"Query: {test_query}")
    print(f"Best Match: {match} (Score: {score:.4f})")
