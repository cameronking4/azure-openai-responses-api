import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_API_MODEL", "gpt-4o")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")

# Validate required environment variables
if not AZURE_OPENAI_API_KEY:
    print("Warning: AZURE_OPENAI_API_KEY environment variable is not set. API calls will fail.")

if not AZURE_OPENAI_ENDPOINT:
    print("Warning: AZURE_OPENAI_ENDPOINT environment variable is not set. API calls will fail.")
