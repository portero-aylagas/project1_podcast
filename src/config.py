"""Shared application configuration.

This module is responsible for loading environment variables and exposing a
single configured OpenAI client for the rest of the application.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is not set. Add it to your environment or to a .env file."
    )

client = OpenAI(api_key=api_key)
