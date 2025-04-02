import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Print environment variables (with API key partially masked)
print("Environment variables:")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model = os.getenv("AZURE_OPENAI_API_MODEL")

print(f"AZURE_OPENAI_API_KEY: {'*' * 5 + api_key[-5:] if api_key else 'Not set'}")
print(f"AZURE_OPENAI_ENDPOINT: {endpoint}")
print(f"AZURE_OPENAI_API_VERSION: {api_version}")
print(f"AZURE_OPENAI_API_MODEL: {model}")

# REMOVED: Hardcoded credentials section to comply with security best practices
# Always use environment variables for sensitive information

# Try with environment variables
try:
    print("\nTrying with environment variables...")
    env_client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    response = env_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, world!"}],
        max_tokens=10
    )
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {str(e)}")

# Try with responses API using environment variables
try:
    print("\nTrying with responses API...")
    response = env_client.responses.create(
        model=model,
        input="Hello, world!"
    )
    print(f"Response: {response.output_text}")
except Exception as e:
    print(f"Error: {str(e)}")
