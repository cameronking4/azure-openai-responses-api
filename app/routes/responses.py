from fastapi import APIRouter, HTTPException, Body, File, UploadFile, Form
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import base64
from openai import AzureOpenAI
import json
import os
import tempfile
from app.config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL, API_VERSION

router = APIRouter()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Models for request and response
class TextRequest(BaseModel):
    input: str
    truncation: Optional[str] = "auto"

class ToolParameter(BaseModel):
    type: str = "object"  # Default to "object" as per OpenAI's schema
    properties: Dict[str, Any]
    required: List[str] = []
    additionalProperties: Optional[bool] = None

class Tool(BaseModel):
    type: str = Field(
        ..., 
        description="Tool type, must be one of the supported values",
        json_schema_extra={
            "examples": ["function", "code_interpreter", "file_search", "web_search"]
        }
    )
    name: str
    description: str
    parameters: ToolParameter
    strict: Optional[bool] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
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
                }
            ]
        }
    }
    
    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # First validate with the standard model validation
        validated = super().model_validate(obj, *args, **kwargs)
        
        # Then check if the type is valid
        valid_types = [
            "function", "code_interpreter", "file_search", "web_search", 
            "web_search_preview", "web_search_preview_2025_03_11", 
            "computer-preview", "computer_use_preview", "bing_grounding", "openapi"
        ]
        
        if validated.type not in valid_types:
            raise ValueError(f"Invalid tool type: {validated.type}. Must be one of: {', '.join(valid_types)}")
        
        return validated

class ToolCallingRequest(BaseModel):
    input: str
    tools: List[Tool]
    truncation: Optional[str] = "auto"

class TextAndImageRequest(BaseModel):
    text: str
    image: str  # Base64 encoded image
    truncation: Optional[str] = "auto"

class ResponseOutput(BaseModel):
    response_id: str
    output: str
    status: str
    usage: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None

@router.post("/text", response_model=ResponseOutput)
async def generate_text_response(request: TextRequest):
    try:
        response = client.responses.create(
            model=AZURE_OPENAI_MODEL,
            input=request.input,
            truncation=request.truncation
        )
        
        # Convert usage to dictionary if it's not already
        usage_dict = response.usage.model_dump() if hasattr(response.usage, "model_dump") else response.usage
        
        return {
            "response_id": response.id,
            "output": response.output_text,
            "status": response.status,
            "usage": usage_dict,
            "raw_response": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Azure OpenAI API: {str(e)}")

@router.post("/tool-calling", response_model=ResponseOutput)
async def generate_tool_calling_response(request: ToolCallingRequest):
    try:
        response = client.responses.create(
            model=AZURE_OPENAI_MODEL,
            input=request.input,
            tools=[tool.model_dump() for tool in request.tools],
            truncation=request.truncation
        )
        
        # Convert usage to dictionary if it's not already
        usage_dict = response.usage.model_dump() if hasattr(response.usage, "model_dump") else response.usage
        
        return {
            "response_id": response.id,
            "output": response.output_text if hasattr(response, "output_text") else str(response.output),
            "status": response.status,
            "usage": usage_dict,
            "raw_response": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Azure OpenAI API: {str(e)}")

@router.post("/text-and-image", response_model=ResponseOutput)
async def generate_text_and_image_response(request: TextAndImageRequest):
    try:
        # Format the input for the Azure OpenAI API
        input_data = [
            {"role": "user", "content": request.text},
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
        
        response = client.responses.create(
            model=AZURE_OPENAI_MODEL,
            input=input_data,
            truncation=request.truncation
        )
        
        # Convert usage to dictionary if it's not already
        usage_dict = response.usage.model_dump() if hasattr(response.usage, "model_dump") else response.usage
        
        return {
            "response_id": response.id,
            "output": response.output_text if hasattr(response, "output_text") else str(response.output),
            "status": response.status,
            "usage": usage_dict,
            "raw_response": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Azure OpenAI API: {str(e)}")

@router.post("/file-search", response_model=ResponseOutput)
async def generate_file_search_response(
    input_text: str = Form(...),
    files: List[UploadFile] = File(..., description="Files to search through (PDF, DOCX, TXT, etc.)"),
    vector_store_name: Optional[str] = Form("Temporary Vector Store", description="Name for the temporary vector store"),
    max_results: Optional[int] = Form(20, description="Maximum number of results to return"),
    delete_after: Optional[bool] = Form(True, description="Whether to delete the vector store after the query"),
    truncation: Optional[str] = Form("auto", description="Truncation strategy")
):
    try:
        # Create a temporary vector store
        vector_store = client.vector_stores.create(
            name=vector_store_name
        )
        
        # Save uploaded files to temporary directory
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        for uploaded_file in files:
            # Create a temporary file path
            file_path = os.path.join(temp_dir, uploaded_file.filename)
            file_paths.append(file_path)
            
            # Save the uploaded file
            with open(file_path, "wb") as f:
                # Read in chunks to handle large files
                chunk_size = 1024 * 1024  # 1MB chunks
                content = await uploaded_file.read(chunk_size)
                while content:
                    f.write(content)
                    content = await uploaded_file.read(chunk_size)
                
                # Reset file position for reading
                await uploaded_file.seek(0)
        
        # Open file streams for upload to Azure OpenAI
        file_streams = [open(path, "rb") for path in file_paths]
        
        try:
            # Upload files to the vector store
            file_batch = client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, 
                files=file_streams
            )
            
            # Query the vector store
            response = client.responses.create(
                model=AZURE_OPENAI_MODEL,
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store.id],
                    "max_num_results": max_results
                }],
                input=input_text,
                truncation=truncation
            )
            
            # Convert usage to dictionary if it's not already
            usage_dict = response.usage.model_dump() if hasattr(response.usage, "model_dump") else response.usage
            
            result = {
                "response_id": response.id,
                "output": response.output_text if hasattr(response, "output_text") else str(response.output),
                "status": response.status,
                "usage": usage_dict,
                "raw_response": response.model_dump()
            }
            
            # Delete the vector store if requested
            if delete_after:
                client.vector_stores.delete(vector_store_id=vector_store.id)
            
            return result
            
        finally:
            # Close file streams
            for file_stream in file_streams:
                file_stream.close()
            
            # Clean up temporary files
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove temporary directory
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Azure OpenAI API: {str(e)}")
