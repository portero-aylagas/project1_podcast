from dotenv import load_dotenv
from openai import OpenAI
import os

# Loading OpenAI API key
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not loaded")

client = OpenAI(api_key=api_key)