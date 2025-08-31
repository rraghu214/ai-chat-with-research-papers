import os
import google.generativeai as genai

# Configure with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Try a simple call
model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Hello Gemini! Summarize what you are in 1 sentence.")

print(response.text)