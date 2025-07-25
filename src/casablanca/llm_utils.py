import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def summarize_content(text, prompt):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        print(f"[LOG] Sending request to Gemini API with prompt: {prompt[:50]}...")
        response = model.generate_content(f"{prompt}\n\nTranscript:\n{text}")
        print("[LOG] Received response from Gemini API.")
        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini API summarization failed: {e}")
        return "Error: Could not generate summary."
