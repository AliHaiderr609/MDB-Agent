def is_academic_query(query_text):
    """
    Checks if a query contains non-academic keywords.
    Returns (is_academic, reason)
    """
    # Standard list of non-academic keywords
    blocked_keywords = ["done", "ok", "yes sir", "present", "whatsapp", "hello", "hi"]
    
    query_lower = query_text.lower()
    
    for kw in blocked_keywords:
        # Check for whole word matches to avoid blocking "present" inside "presentation"
        import re
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, query_lower):
            return False, f"Non-academic keyword detected: '{kw}'"
            
    return True, None

if __name__ == "__main__":
    test_queries = [
        "Explain primary memory",
        "i am present sir",
        "done",
        "can you help with whatsapp group?",
        "What is a presentation?"
    ]
    
    for q in test_queries:
        is_acad, reason = is_academic_query(q)
        status = "PASSED" if is_acad else f"BLOCKED ({reason})"
        print(f"Query: '{q}' -> {status}")
