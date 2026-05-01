import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and cleans extra whitespace.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # 1. Normalize line endings
        text = text.replace('\r\n', '\n')
        
        # 2. Normalize paragraph breaks (multiple \n -> single \n)
        text = re.sub(r'\n\s*\n+', '\n', text)
        
        # 3. Clean up single newlines that are just line-wraps within paragraphs
        # Rule: If a line doesn't end with a sentence-ending punctuation, we might join it.
        # But for handouts, it's often better to just fix multiple spaces and trust \n.
        text = re.sub(r'[ \t]+', ' ', text) # Normalize spaces
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

if __name__ == "__main__":
    # Test with the user manual if it exists
    import os
    test_path = os.path.join(os.path.dirname(__file__), "..", "user manual.pdf")
    if os.path.exists(test_path):
        print("Extracting test text from user manual...")
        content = extract_text_from_pdf(test_path)
        print(f"Extracted {len(content)} characters.")
        print(f"Sample: {content[:150]}...")
    else:
        print("Test PDF not found.")
