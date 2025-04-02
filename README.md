# Azure OpenAI Responses API

A simple Python API that interfaces with Azure OpenAI's Responses API. This API supports text, tool calling, and text+image inputs. Based on example code from https://github.com/guygregory/Responses-API/tree/main

## Features

- **Text Endpoint**: Send text prompts to Azure OpenAI
- **Tool Calling Endpoint**: Use function calling capabilities
- **Text and Image Endpoint**: Process multimodal inputs with text and images
- **File Search Endpoint**: Upload files and ask questions about them

## Implementation Note

The API supports:
- Text generation
- Tool calling
- Text and image inputs
- File search
- Vector store management

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example` and add your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
   AZURE_OPENAI_MODEL=gpt-4o
   API_VERSION=2025-03-01-preview
   ```

## Running the API

Start the API server:

```
python run.py
```

Or with uvicorn directly:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Text Input

```
POST /api/text
```

Request body:
```json
{
  "input": "Your text prompt here"
}
```

Response:
```json
{
  "response_id": "resp_67cb32528d6881909eb2859a55e18a85",
  "output": "Response from Azure OpenAI",
  "status": "completed",
  "usage": {
    "input_tokens": 20,
    "output_tokens": 11,
    "total_tokens": 31
  },
  "raw_response": {
    "id": "resp_67cb32528d6881909eb2859a55e18a85",
    "output_text": "Response from Azure OpenAI",
    "status": "completed",
    "usage": {
      "input_tokens": 20,
      "output_tokens": 11,
      "total_tokens": 31
    }
  }
}
```

### File Search

```
POST /api/file-search
```

This endpoint accepts multipart form data with file uploads and uses Azure OpenAI's file search capability to answer questions based on the uploaded files.

Request parameters (multipart form):
- `input_text` (required): The query or question to ask about the files
- `files` (required): One or more files to upload and search
- `vector_store_name` (optional): Name for the temporary vector store (default: "Temporary Vector Store")
- `max_results` (optional): Maximum number of results to return (default: 20)
- `delete_after` (optional): Whether to delete the vector store after the query (default: true)
- `truncation` (optional): Truncation strategy (default: "auto")

Example usage:
```python
import requests

url = "http://localhost:8000/api/file-search"

# Open the file for upload
with open("document.pdf", "rb") as f:
    # Create the form data
    files = {"files": ("document.pdf", f)}
    data = {
        "input_text": "What are the key points in this document?",
        "vector_store_name": "My Document Store",
        "max_results": 10,
        "delete_after": True
    }
    
    # Make the request
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(result["output"])
```

Test scripts are provided to demonstrate this functionality:
```
python test_file_search.py           # Basic file search example
python advanced_file_search_example.py  # Advanced example with multiple file types
```

The advanced example includes:
- A reusable `FileSearchClient` class for easy integration
- Support for multiple file types (txt, md, json, etc.)
- Sample files created on-the-fly for testing
- Multiple query examples to demonstrate capabilities

### Tool Calling

```
POST /api/tool-calling
```

Request body:
```json
{
  "input": "What's the weather in San Francisco?",
  "tools": [
    {
      "type": "function",
      "name": "get_weather",
      "description": "Get weather for location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string"}
        },
        "required": ["location"]
      }
    }
  ]
}
```

#### Supported Tool Types

The `type` field in the tool object must be one of the following supported values:

- `function` - For function calling
- `code_interpreter` - For code interpretation
- `file_search` - For searching files
- `web_search` - For web search
- `web_search_preview` - For web search preview
- `web_search_preview_2025_03_11` - For web search preview (2025-03-11 version)
- `computer-preview` - For computer preview
- `computer_use_preview` - For computer use preview
- `bing_grounding` - For Bing grounding
- `openapi` - For OpenAPI specification

#### Testing Tool Calling

You can test the tool calling functionality using the provided `test_tool_calling.py` script:

```
python test_tool_calling.py
```

This script tests both the local API server and makes a direct call to the Azure OpenAI API to verify that tool calling works correctly.

#### Example Clients

Several example client implementations are provided:

1. **Basic Client** (`example_tool_calling_client.py`):
   ```
   python example_tool_calling_client.py
   ```
   This script demonstrates how to use the tool calling API with different types of tools:
   - Weather tool (function type)
   - Calculator tool (function type)
   - Search tool (web_search type)
   - Multiple tools in a single request

2. **Complete Tool Calling Example** (`complete_tool_calling_example.py`):
   ```
   python complete_tool_calling_example.py
   ```
   This script demonstrates a complete tool calling workflow:
   - Making the initial request to the API
   - Parsing tool calls from the response
   - Executing the tools with the provided arguments
   - Sending the tool results back to the API
   - Displaying the final response

   This example is particularly useful for understanding how to implement a full tool calling conversation flow with Azure OpenAI.

### Text and Image

```
POST /api/text-and-image
```

Request body:
```json
{
  "text": "What's in this image?",
  "image": "base64_encoded_image_string"
}
```

## Integration with NextJS

To integrate with a NextJS frontend, you can make fetch requests to these endpoints. For example:

```javascript
// Example NextJS API call
const response = await fetch('http://localhost:8000/api/text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    input: 'Your prompt here'
  }),
});

const data = await response.json();
```

## Documentation

Interactive API documentation is available at http://localhost:8000/docs
