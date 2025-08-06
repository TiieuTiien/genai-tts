def log_gemini_error(e, context="", file_path=""):
    """Simple logger for Gemini API errors."""
    
    if file_path:
        print(f"❌ Error {context} for {file_path}:")
    else:
        print(f"❌ Error {context}:")
    
    # Handle nested error object
    print(f"   Errors: {e}")