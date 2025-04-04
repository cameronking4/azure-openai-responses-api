import os
import io
import json
import uuid
import math
import base64
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
from openai import AzureOpenAI, AsyncAzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Progress tracking for large files
file_progress = {}

# Initialize FastAPI app
app = FastAPI(title="Azure OpenAI Responses API")

# Initialize Azure OpenAI client
try:
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_API_ENDPOINT"]
    )
except KeyError as e:
    print(f"Missing environment variable: {e}")
    print("Please ensure all required environment variables are set in .env file")
    raise

# Request models
class BasicPromptRequest(BaseModel):
    prompt: str

class ConversationRequest(BaseModel):
    messages: List[Dict[str, str]]

class ChainedRequest(BaseModel):
    input: str
    previous_response_id: Optional[str] = None

class ManualChainRequest(BaseModel):
    inputs: List[Dict[str, str]]

class ImageRequest(BaseModel):
    prompt: str
    image: str  # base64 encoded image

class ImageUrlRequest(BaseModel):
    prompt: str
    url: HttpUrl

class WeatherRequest(BaseModel):
    location: str
    unit: str = "celsius"

class StreamRequest(BaseModel):
    prompt: str

class FileSearchRequest(BaseModel):
    query: str
    file_paths: List[str]
    max_results: int = 20
    chunk_size: int = 1024 * 1024  # Default 1MB chunks

class LargeFileSearchRequest(BaseModel):
    query: str
    file_paths: List[str]
    max_results: int = 20
    chunk_size: int = 1024 * 1024  # Default 1MB chunks
    batch_size: int = 5  # Number of chunks to process at once

class StructuredRequest(BaseModel):
    input: str
    json_schema: Dict[str, Any]  # Renamed from schema to avoid conflict with BaseModel

# Initialize async client
async_client = AsyncAzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_API_ENDPOINT"]
)

# Basic completion endpoint
@app.post("/basic")
async def basic_completion(request: BasicPromptRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=request.prompt
        )
        return {"response": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Conversation endpoint
@app.post("/conversation")
async def conversation(request: ConversationRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=request.messages
        )
        return {"response": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image analysis endpoint
@app.post("/image")
async def analyze_image(request: ImageRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=[
                {"role": "user", "content": request.prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{request.image}"
                        }
                    ]
                }
            ]
        )
        return {"response": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image URL analysis endpoint
@app.post("/image-url")
async def analyze_image_url(request: ImageUrlRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=[
                {"role": "user", "content": request.prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": str(request.url)
                        }
                    ]
                }
            ]
        )
        return {"response": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Weather function endpoint
@app.post("/weather")
async def get_weather(request: WeatherRequest):
    try:
        tools = [{
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
        }]
        
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=[{"role": "user", "content": f"What's the weather like in {request.location}?"}],
            tools=tools
        )
        
        tool_call = response.output[0]
        args = json.loads(tool_call.arguments)
        
        # Here you would call your actual weather API with the coordinates
        # For now, returning a mock response
        return {
            "location": request.location,
            "coordinates": {"lat": args["latitude"], "lon": args["longitude"]},
            "unit": request.unit,
            "temperature": "22°C"  # Mock value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stream endpoint
@app.post("/stream")
async def stream_completion(request: StreamRequest):
    try:
        async def generate():
            stream = client.responses.create(
                model=os.environ["AZURE_OPENAI_API_MODEL"],
                input=request.prompt,
                stream=True
            )
            for event in stream:
                if event.type == 'response.output_text.delta':
                    yield f"data: {json.dumps({'delta': event.delta})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stream SSE endpoint
@app.post("/stream-sse")
async def stream_sse(request: StreamRequest):
    try:
        async def generate():
            stream = client.responses.create(
                model=os.environ["AZURE_OPENAI_API_MODEL"],
                input=request.prompt,
                stream=True
            )
            for event in stream:
                if event.type == 'response.created':
                    yield f"event: created\ndata: {json.dumps({'id': event.response.id})}\n\n"
                elif event.type == 'response.output_text.delta':
                    yield f"event: delta\ndata: {json.dumps({'text': event.delta})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Conversation stream endpoint
@app.post("/conversation-stream")
async def conversation_stream(request: ConversationRequest):
    try:
        async def generate():
            stream = client.responses.create(
                model=os.environ["AZURE_OPENAI_API_MODEL"],
                input=request.messages,
                stream=True
            )
            for event in stream:
                if event.type == 'response.created':
                    yield f"event: created\ndata: {json.dumps({'id': event.response.id})}\n\n"
                elif event.type == 'response.output_text.delta':
                    yield f"event: delta\ndata: {json.dumps({'text': event.delta})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stream async endpoint
@app.post("/stream-async")
async def stream_async(request: StreamRequest):
    try:
        async def generate():
            stream = await async_client.responses.create(
                model=os.environ["AZURE_OPENAI_API_MODEL"],
                input=request.prompt,
                stream=True
            )
            async for event in stream:
                if hasattr(event, "delta") and event.delta:
                    yield f"data: {json.dumps({'delta': event.delta})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File search endpoint
@app.post("/filesearch")
async def file_search(request: FileSearchRequest):
    try:
        # Create a vector store
        vector_store = client.vector_stores.create(
            name="Search Documents"
        )

        # Upload files
        file_streams = [open(path, "rb") for path in request.file_paths]
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams
        )

        # Query the vector store
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store.id],
                "max_num_results": request.max_results
            }],
            input=request.query
        )

        # Cleanup
        for stream in file_streams:
            stream.close()
        client.vector_stores.delete(vector_store_id=vector_store.id)

        return {"response": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Structured output endpoint
@app.post("/structured")
async def structured_output(request: StructuredRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=[
                {"role": "system", "content": "Extract structured information."},
                {"role": "user", "content": request.input}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "structured_data",
                    "schema": request.json_schema,
                    "strict": True
                }
            }
        )
        return {"response": json.loads(response.output_text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Large file search endpoint with chunking and progress tracking
@app.post("/large-filesearch")
async def large_file_search(request: LargeFileSearchRequest):
    try:
        search_id = str(uuid.uuid4())
        file_progress[search_id] = {
            "total_chunks": 0,
            "processed_chunks": 0,
            "status": "initializing"
        }

        # Create a vector store
        vector_store = client.vector_stores.create(
            name=f"Large Search Documents {search_id}"
        )

        # Calculate total chunks for all files
        total_chunks = 0
        for file_path in request.file_paths:
            file_size = os.path.getsize(file_path)
            total_chunks += math.ceil(file_size / request.chunk_size)
        
        file_progress[search_id]["total_chunks"] = total_chunks
        file_progress[search_id]["status"] = "processing"

        results = []
        for file_path in request.file_paths:
            with open(file_path, 'rb') as file:
                chunk_batches = []
                current_batch = []
                
                while True:
                    chunk = file.read(request.chunk_size)
                    if not chunk:
                        break
                    
                    current_batch.append(chunk)
                    if len(current_batch) >= request.batch_size:
                        chunk_batches.append(current_batch)
                        current_batch = []
                
                if current_batch:
                    chunk_batches.append(current_batch)

                for batch in chunk_batches:
                    # Process batch of chunks
                    file_batch = client.vector_stores.file_batches.upload_and_poll(
                        vector_store_id=vector_store.id,
                        files=[io.BytesIO(chunk) for chunk in batch]
                    )
                    
                    # Update progress
                    file_progress[search_id]["processed_chunks"] += len(batch)
                    
                    # Query the vector store for this batch
                    response = client.responses.create(
                        model=os.environ["AZURE_OPENAI_API_MODEL"],
                        tools=[{
                            "type": "file_search",
                            "vector_store_ids": [vector_store.id],
                            "max_num_results": request.max_results
                        }],
                        input=request.query
                    )
                    
                    if response.output_text.strip():
                        results.append(response.output_text)

        # Cleanup
        client.vector_stores.delete(vector_store_id=vector_store.id)
        
        file_progress[search_id]["status"] = "completed"
        
        # Combine and summarize results
        combined_results = "\n\n".join(results)
        final_response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=f"Summarize and combine these search results about '{request.query}':\n\n{combined_results}"
        )

        return {
            "search_id": search_id,
            "status": "completed",
            "response": final_response.output_text
        }

    except Exception as e:
        if search_id in file_progress:
            file_progress[search_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=str(e))

# Get search progress endpoint
@app.get("/large-filesearch/{search_id}/progress")
async def get_search_progress(search_id: str):
    if search_id not in file_progress:
        raise HTTPException(status_code=404, detail="Search ID not found")
    
    progress = file_progress[search_id]
    percentage = (progress["processed_chunks"] / progress["total_chunks"] * 100) if progress["total_chunks"] > 0 else 0
    
    return {
        "search_id": search_id,
        "status": progress["status"],
        "progress_percentage": round(percentage, 2),
        "processed_chunks": progress["processed_chunks"],
        "total_chunks": progress["total_chunks"]
    }

# Chained response endpoint using previous_response_id
@app.post("/chained-response")
async def chained_response(request: ChainedRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=request.input,
            previous_response_id=request.previous_response_id
        )
        return {
            "response_id": response.id,
            "response": response.output_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Manual chained response endpoint using message history
@app.post("/manual-chain")
async def manual_chain(request: ManualChainRequest):
    try:
        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_API_MODEL"],
            input=request.inputs
        )
        return {
            "response_id": response.id,
            "response": response.output_text,
            "full_message_history": request.inputs + [
                {
                    "role": "assistant",
                    "content": response.output_text
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
