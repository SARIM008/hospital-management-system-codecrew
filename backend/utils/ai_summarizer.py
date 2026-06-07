import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AISummarizer:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = None
        
        if not self.api_key:
            print("WARNING: DEEPSEEK_API_KEY not found in environment variables. AI features will be disabled.")
            return
        
        try:
            # DeepSeek is OpenAI-compatible
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
        except Exception as e:
            print(f"ERROR: Failed to initialize OpenAI client: {str(e)}")
            self.client = None

    def summarize_consultation(self, transcript_text):
        """
        Takes a raw transcript and returns a structured dictionary for the OPDVisit model.
        """
        if not transcript_text or not self.client:
            return None

        system_prompt = (
            "You are a professional medical scribe. Your task is to analyze clinical consultation transcripts "
            "and extract structured information into a specific JSON format. "
            "Focus on medical accuracy and clarity."
        )

        user_prompt = (
            f"Please analyze the following consultation transcript and extract the key information:\n\n"
            f"TRANSCRIPT:\n\"\"\"\n{transcript_text}\n\"\"\"\n\n"
            "Return a JSON object with the following fields:\n"
            "1. 'complaints': A concise summary of the patient's symptoms and reasons for the visit.\n"
            "2. 'diagnosis': The clinical diagnosis or suspected condition mentioned by the doctor.\n"
            "3. 'doctor_notes': Any additional clinical notes, observations, or advice given during the visit.\n"
            "4. 'medicines': A list of objects with 'name', 'dosage', and 'duration' if any medications were prescribed.\n\n"
            "IMPORTANT: Return ONLY the raw JSON object. Do not include markdown formatting or explanations."
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={'type': 'json_object'},
                stream=False
            )

            result_content = response.choices[0].message.content
            return json.loads(result_content)
        except Exception as e:
            print(f"Error during AI summarization: {str(e)}")
            return None

# Singleton instance
ai_summarizer = AISummarizer()
