import os
import requests
import json
import math
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model = os.getenv("AZURE_OPENAI_API_MODEL")

# Remove trailing slash from endpoint if present
if endpoint and endpoint.endswith('/'):
    endpoint = endpoint[:-1]

# Construct the URL for the responses API
responses_url = f"{endpoint}/openai/deployments/{model}/responses?api-version={api_version}"

# Set up headers
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# Define tool implementations
def get_weather(latitude, longitude):
    """
    Simulate getting weather data for the given coordinates.
    In a real application, this would call a weather API.
    """
    # This is a mock implementation
    weather_data = {
        "temperature": 22.5,
        "conditions": "Partly Cloudy",
        "humidity": 65,
        "wind_speed": 10.2
    }
    return weather_data

def calculate(expression):
    """
    Evaluate a mathematical expression.
    """
    try:
        # Warning: eval can be dangerous in production code
        # This is just for demonstration purposes
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# Define the tools
tools = [
    {
        "type": "function",
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
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Perform a mathematical calculation.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
]

def main():
    # Step 1: Make the initial request
    user_input = "What's the weather in London (51.5074, -0.1278) and calculate 15 * 7 + 22"
    
    print(f"User: {user_input}")
    print("\nSending initial request to Azure OpenAI API...")
    
    # Define the input message
    input_message = [{"role": "user", "content": user_input}]
    
    # Define the request payload
    payload = {
        "input": input_message,
        "tools": tools
    }
    
    # Make the request
    response = requests.post(responses_url, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    response_data = response.json()
    
    # Step 2: Parse the tool calls
    output = response_data.get("output", [])
    if not output or not isinstance(output, list) or len(output) == 0:
        print("No output received")
        return
    
    first_output = output[0]
    tool_calls = first_output.get("tool_calls", [])
    
    if not tool_calls:
        print("No tool calls received")
        print(f"Response: {first_output.get('content', '')}")
        return
    
    # Step 3: Execute the tools
    print("\nTool calls received:")
    
    tool_results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_id = tool_call.get("id")
        tool_args = json.loads(tool_call.get("arguments", "{}"))
        
        print(f"\nExecuting tool: {tool_name}")
        print(f"Arguments: {tool_args}")
        
        # Execute the appropriate tool
        result = None
        if tool_name == "get_weather":
            result = get_weather(tool_args.get("latitude"), tool_args.get("longitude"))
        elif tool_name == "calculate":
            result = calculate(tool_args.get("expression"))
        
        print(f"Result: {result}")
        
        # Add the result to the list
        tool_results.append({
            "type": "function_call_output",
            "call_id": tool_id,
            "output": json.dumps(result)
        })
    
    # Step 4: Send the tool results back to the API
    print("\nSending tool results back to Azure OpenAI API...")
    
    # Add the original message, the assistant's tool calls, and the tool results to the conversation
    conversation = input_message + [first_output] + tool_results
    
    # Define the request payload
    payload = {
        "input": conversation,
        "tools": tools
    }
    
    # Make the request
    response = requests.post(responses_url, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    response_data = response.json()
    
    # Step 5: Display the final response
    output = response_data.get("output", [])
    if not output or not isinstance(output, list) or len(output) == 0:
        print("No output received")
        return
    
    final_response = output[0].get("content", "")
    print("\nFinal response:")
    print(final_response)

if __name__ == "__main__":
    main()
