import os
from dotenv import load_dotenv

load_dotenv()

# Model parameters
TEMPERATURE=0.5
MAX_TOKENS=256
CREDENTIAL=os.getenv("OPENAI_API_KEY")

# Model IDs
GPT4_MINI_MODEL_ID = "gpt-4.1-mini"
GPT5_MINI_MODEL_ID = "gpt-5-mini"