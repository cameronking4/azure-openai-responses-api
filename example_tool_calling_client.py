import requests
import json

def call_tool_calling_api(input_text, tools):
    """
    Call the tool calling API with the given input text and tools.
    
    Args:
        input_text (str): The input text to send to the API
        tools (list): A list of tool objects
        
    Returns:
        dict: The API response
    """
    url = "http://localhost:8000/api/tool-calling"
    
    payload = {
        "input": input_text,
        "tools": tools,
        "truncation": "auto"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def main():
    # Example 1: Weather tool
    weather_tool = {
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
    }
    
    # Example 2: Calculator tool
    calculator_tool = {
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
    
    # Example 3: Search tool
    search_tool = {
        "type": "web_search",
        "name": "search",
        "description": "Search the web for information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    }
    
    # Example queries
    queries = [
        {
            "input": "What's the weather like in London?",
            "tools": [weather_tool]
        },
        {
            "input": "Calculate 15 * 7 + 22",
            "tools": [calculator_tool]
        },
        {
            "input": "What's the capital of France?",
            "tools": [search_tool]
        },
        {
            "input": "I need weather information and to do a calculation.",
            "tools": [weather_tool, calculator_tool]
        }
    ]
    
    # Run each query
    for i, query in enumerate(queries):
        print(f"\nExample {i+1}: {query['input']}")
        print(f"Tools: {', '.join(tool['name'] for tool in query['tools'])}")
        
        response = call_tool_calling_api(query['input'], query['tools'])
        
        if response:
            print("\nResponse:")
            print(f"Output: {response['output']}")
            print(f"Status: {response['status']}")
            
            # Print tool calls if available in the raw response
            if 'raw_response' in response and 'output' in response['raw_response']:
                output = response['raw_response']['output']
                if isinstance(output, list) and len(output) > 0 and 'tool_calls' in output[0]:
                    print("\nTool Calls:")
                    for tool_call in output[0]['tool_calls']:
                        print(f"Tool: {tool_call['name']}")
                        print(f"Arguments: {tool_call['arguments']}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
