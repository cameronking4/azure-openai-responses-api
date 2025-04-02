from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import base64
from openai import AzureOpenAI
import json
import os
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
    type: str
    properties: Dict[str, Any]
    required: List[str] = []

class Tool(BaseModel):
    type: str
    name: str
    description: str
    parameters: ToolParameter

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
        
        return {
            "response_id": response.id,
            "output": response.output_text,
            "status": response.status,
            "usage": response.usage,
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
        
        return {
            "response_id": response.id,
            "output": response.output_text if hasattr(response, "output_text") else str(response.output),
            "status": response.status,
            "usage": response.usage,
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
        
        return {
            "response_id": response.id,
            "output": response.output_text if hasattr(response, "output_text") else str(response.output),
            "status": response.status,
            "usage": response.usage,
            "raw_response": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Azure OpenAI API: {str(e)}")
