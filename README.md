# Azure OpenAI Responses API

A simple Python API that interfaces with Azure OpenAI's Responses API. This API supports text, tool calling, and text+image inputs.

## Features

- **Text Endpoint**: Send text prompts to Azure OpenAI
- **Tool Calling Endpoint**: Use function calling capabilities
- **Text and Image Endpoint**: Process multimodal inputs with text and images

## Implementation Note

This API provides a mock implementation of the Azure OpenAI Responses API for development and testing purposes. The mock implementation simulates the behavior of the real API without making actual calls to Azure OpenAI.

When you're ready to use the real Azure OpenAI API, you can uncomment the real client initialization in `app/routes/responses.py` and ensure your Azure OpenAI credentials are correctly set in the `.env` file.

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
