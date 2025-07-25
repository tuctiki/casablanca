import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_video_category(title, description, categories):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable not set.")
            raise ValueError("GEMINI_API_KEY environment variable not set.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        category_list_str = ", ".join(categories)
        prompt = f"""
        Given the following video title and description, classify the video into one of these categories: {category_list_str}.
        If none of the categories apply, respond with "Other".
        Respond with only the category name.

        Title: {title}
        Description: {description}
        """
        logging.info(f"Sending request to Gemini API for video categorization...")
        response = model.generate_content(prompt)
        logging.info("Received response from Gemini API for video categorization.")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini API video categorization failed: {e}")
        return "Error"

def summarize_content(text, prompt):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable not set.")
            raise ValueError("GEMINI_API_KEY environment variable not set.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        logging.info(f"Sending request to Gemini API with prompt: {prompt[:50]}...")
        response = model.generate_content(f"{prompt}\n\nTranscript:\n{text}")
        logging.info("Received response from Gemini API.")
        return response.text
    except Exception as e:
        logging.error(f"Gemini API summarization failed: {e}")
        return "Error: Could not generate summary."
