from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("ERROR: GROQ_API_KEY not set in environment")
else:
    try:
        client = Groq(api_key=api_key)
        models = client.models.list()
        print("Available Groq models:")
        for model in models.data:
            print(f"  - {model.id}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
