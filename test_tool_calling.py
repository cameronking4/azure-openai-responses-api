import os
import requests
import json
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

# Test the local API server
print("\nTesting local API server tool-calling endpoint...")

# Define a sample tool with the correct type
tool = {
    "type": "function",  # This must be one of the supported values
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"]
    }
}

# Define the request payload
payload = {
    "input": "What's the weather like in London?",
    "tools": [tool],
    "truncation": "auto"
}

try:
    # Make a request to the local API server
    response = requests.post(
        "http://localhost:8000/api/tool-calling",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Response: Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

# Test direct Azure OpenAI API call
print("\nTesting direct Azure OpenAI API call...")

# Remove trailing slash from endpoint if present
if endpoint and endpoint.endswith('/'):
    endpoint = endpoint[:-1]

# Construct the URL for the responses API
responses_url = f"{endpoint}/openai/deployments/{model}/responses?api-version={api_version}"
print(f"Responses URL: {responses_url}")

# Set up headers
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

try:
    # Define the input message
    input_message = [{"role": "user", "content": "What's the weather like in London?"}]
    
    # Define the request payload for the direct API call
    direct_payload = {
        "input": input_message,
        "tools": [tool]
    }
    
    # Make a direct request to the Azure OpenAI API
    response = requests.post(responses_url, headers=headers, json=direct_payload, timeout=30)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Response: Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
