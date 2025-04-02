import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Print environment variables
print("Environment variables:")
print(f"AZURE_OPENAI_API_KEY: {'*' * 5 + os.getenv('AZURE_OPENAI_API_KEY')[-5:] if os.getenv('AZURE_OPENAI_API_KEY') else 'Not set'}")
print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
print(f"AZURE_OPENAI_API_MODEL: {os.getenv('AZURE_OPENAI_API_MODEL')}")

try:
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    print("\nClient initialized successfully")
    
    # Try to make a simple request to check connectivity using chat completions
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_API_MODEL"),
            messages=[{"role": "user", "content": "Hello, world!"}],
            max_tokens=10
        )
        print("\nChat completion response:")
        print(f"Response: {response.choices[0].message.content}")
        print("Chat completion successful!")
    except Exception as e:
        print(f"\nError creating chat completion: {str(e)}")
    
    # Try to make a simple request to check connectivity using responses API
    try:
        response = client.responses.create(
            model=os.getenv("AZURE_OPENAI_API_MODEL"),
            input="Hello, world!"
        )
        print("\nResponses API response:")
        print(f"Response: {response.output_text}")
        print("Responses API successful!")
    except Exception as e:
        print(f"\nError creating response: {str(e)}")
        
except Exception as e:
    print(f"\nError initializing client: {str(e)}")
