# Azure OpenAI Responses API

A FastAPI application that provides various endpoints for interacting with Azure OpenAI's services, including text completion, conversation, image analysis, and more.

## Features

- Basic text completion
- Conversation handling
- Image analysis (base64 and URL)
- Weather function calling
- Streaming responses (SSE and async)
- File search with vector store
- Structured output with JSON schema

## Prerequisites

- Python 3.9+
- Azure OpenAI API access
- Azure OpenAI model deployment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Responses-API.git
cd Responses-API
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.sample .env
```
Edit `.env` with your Azure OpenAI credentials:
```
AZURE_OPENAI_API_MODEL=your-model-deployment-name
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-03-01-preview
```

## Running the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`. Access the interactive API documentation at `http://localhost:8000/docs`.

## API Endpoints

### Basic Endpoints

#### POST /basic
Basic text completion endpoint.
```json
{
    "prompt": "Complete this sentence: The quick brown fox"
}
```

#### POST /conversation
Conversation completion with message history.
```json
{
    "messages": [
        {"role": "user", "content": "What is the capital of France?"}
    ]
}
```

#### POST /image
Image analysis with base64-encoded image.
```json
{
    "prompt": "Describe this image",
    "image": "base64_encoded_image_data"
}
```

#### POST /image-url
Image analysis with URL.
```json
{
    "prompt": "Describe this image",
    "url": "https://example.com/image.jpg"
}
```

#### POST /weather
Weather information using function calling.
```json
{
    "location": "London",
    "unit": "celsius"
}
```

### Streaming Endpoints

#### POST /stream
Basic streaming response.
```json
{
    "prompt": "Write a story about"
}
```

#### POST /stream-sse
Server-Sent Events streaming.
```json
{
    "prompt": "Write a story about"
}
```

#### POST /stream-async
Asynchronous streaming response.
```json
{
    "prompt": "Write a story about"
}
```

#### POST /conversation-stream
Streaming conversation response.
```json
{
    "messages": [
        {"role": "user", "content": "Tell me a story"}
    ]
}
```

### Chained Response Endpoints

#### POST /chained-response
Response chaining using previous_response_id.
```json
{
    "input": "Explain this at a level that could be understood by a college freshman",
    "previous_response_id": "resp_67cbc9705fc08190bbe455c5ba3d6daf"
}
```

Response:
```json
{
    "response_id": "resp_67cbc970fd0881908353a4298996b3f6",
    "response": "Here's a simpler explanation..."
}
```

#### POST /manual-chain
Manual response chaining using message history.
```json
{
    "inputs": [
        {
            "role": "user",
            "content": "Define and explain the concept of catastrophic forgetting?"
        },
        {
            "role": "assistant",
            "content": "Catastrophic forgetting refers to..."
        },
        {
            "role": "user",
            "content": "Explain this at a level that could be understood by a college freshman"
        }
    ]
}
```

Response:
```json
{
    "response_id": "resp_67cbc970fd0881908353a4298996b3f6",
    "response": "Let me explain it simply...",
    "full_message_history": [
        // Previous messages plus the new response
    ]
}
```

Implementation Notes for Chained Responses:
- Use `/chained-response` when you want to:
  - Keep the context lightweight
  - Don't need to modify previous messages
  - Have a simple request/response flow
- Use `/manual-chain` when you want to:
  - Have full control over the message history
  - Modify or filter previous messages
  - Keep track of the full conversation history

Example Usage:
```python
# First request to get initial response
response1 = requests.post(
    "https://api.example.com/chained-response",
    json={"input": "Define quantum computing"}
)
first_response = response1.json()

# Second request using previous response ID
response2 = requests.post(
    "https://api.example.com/chained-response",
    json={
        "input": "Explain it more simply",
        "previous_response_id": first_response["response_id"]
    }
)
```

### Specialized Endpoints

#### POST /filesearch
Vector store-based file search for smaller files.
```json
{
    "query": "What are the company values?",
    "file_paths": ["document1.pdf", "document2.pdf"],
    "max_results": 20,
    "chunk_size": 1048576  // Optional, default 1MB
}
```

Response:
```json
{
    "response": "Based on the documents, the company values include..."
}
```

#### POST /large-filesearch
Chunked processing for large files with progress tracking.
```json
{
    "query": "What are the company policies?",
    "file_paths": ["large_handbook.pdf"],
    "max_results": 5,
    "chunk_size": 524288,    // Optional, default 1MB (1024 * 1024)
    "batch_size": 2          // Optional, default 5 chunks per batch
}
```

Response:
```json
{
    "search_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "response": "Summary of company policies found in the document..."
}
```

#### GET /large-filesearch/{search_id}/progress
Track progress of large file processing.

Response:
```json
{
    "search_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress_percentage": 45.5,
    "processed_chunks": 5,
    "total_chunks": 11
}
```

Implementation Notes:
- Status values: "initializing", "processing", "completed", "failed"
- Progress tracking is maintained server-side
- Files are processed in chunks to manage memory
- Results are automatically summarized

#### POST /structured
Structured output with JSON schema validation.
```json
{
    "input": "Extract event: Meeting with John on Monday at 2 PM",
    "json_schema": {
        "type": "object",
        "properties": {
            "event": {"type": "string"},
            "person": {"type": "string"},
            "day": {"type": "string"},
            "time": {"type": "string"}
        }
    }
}
```

## Error Handling

All endpoints include proper error handling and will return appropriate HTTP status codes:

- 200: Successful response
- 400: Bad request (invalid input)
- 404: Resource not found (invalid search_id)
- 500: Server error (Azure OpenAI API issues)

## Implementation Guidelines

### File Processing
- Use `/filesearch` for files < 1MB
- Use `/large-filesearch` for files > 1MB
- Monitor progress using the `/large-filesearch/{search_id}/progress` endpoint
- Consider batch_size based on your server's capabilities:
  - Lower batch_size (1-2): Less memory usage, slower processing
  - Higher batch_size (5-10): More memory usage, faster processing

### Best Practices
1. File Size Handling:
   ```python
   # Check file size before processing
   file_size = os.path.getsize(file_path)
   if file_size > 1024 * 1024:  # 1MB
       use_large_filesearch = True
   ```

2. Progress Monitoring:
   ```python
   # JavaScript example
   async function monitorProgress(searchId) {
     while (true) {
       const response = await fetch(`/large-filesearch/${searchId}/progress`);
       const progress = await response.json();
       
       if (progress.status === 'completed' || progress.status === 'failed') {
         break;
       }
       
       console.log(`Progress: ${progress.progress_percentage}%`);
       await new Promise(resolve => setTimeout(resolve, 1000));
     }
   }
   ```

3. Error Handling:
   ```python
   try:
       response = await fetch('/large-filesearch', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
               query: "search query",
               file_paths: ["large_file.pdf"],
               chunk_size: 524288,
               batch_size: 2
           })
       });
       
       if (!response.ok) {
           const error = await response.json();
           console.error(`Error: ${error.detail}`);
       }
   } catch (error) {
       console.error('Network error:', error);
   }
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
