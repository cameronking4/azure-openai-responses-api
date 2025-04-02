import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model = os.getenv("AZURE_OPENAI_API_MODEL")

# Print environment variables
print("Environment variables:")
print(f"AZURE_OPENAI_API_KEY: {'*' * 5 + api_key[-5:] if api_key else 'Not set'}")
print(f"AZURE_OPENAI_ENDPOINT: {endpoint}")
print(f"AZURE_OPENAI_API_VERSION: {api_version}")
print(f"AZURE_OPENAI_API_MODEL: {model}")

# Remove trailing slash from endpoint if present
if endpoint and endpoint.endswith('/'):
    endpoint = endpoint[:-1]

# Construct the URL for the chat completions API
chat_url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
print(f"\nChat completions URL: {chat_url}")

# Construct the URL for the responses API
responses_url = f"{endpoint}/openai/deployments/{model}/responses?api-version={api_version}"
print(f"Responses URL: {responses_url}")

# Set up headers
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# Try chat completions API
try:
    print("\nTesting chat completions API...")
    chat_data = {
        "messages": [{"role": "user", "content": "Hello, world!"}],
        "max_tokens": 10
    }
    
    response = requests.post(chat_url, headers=headers, json=chat_data, timeout=10)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Response: Success!")
        print(response.json())
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

# Try responses API
try:
    print("\nTesting responses API...")
    responses_data = {
        "input": "Hello, world!"
    }
    
    response = requests.post(responses_url, headers=headers, json=responses_data, timeout=10)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Response: Success!")
        print(response.json())
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
