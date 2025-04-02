import requests
import os
import tempfile
import base64
from typing import List, Optional

class FileSearchClient:
    """
    A client for the file search API that supports multiple file types and advanced options.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the file search client.
        
        Args:
            base_url: The base URL of the API server
        """
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/file-search"
    
    def search(
        self,
        query: str,
        file_paths: List[str],
        vector_store_name: Optional[str] = "Temporary Vector Store",
        max_results: Optional[int] = 20,
        delete_after: Optional[bool] = True,
        truncation: Optional[str] = "auto"
    ):
        """
        Search for information in the provided files.
        
        Args:
            query: The query or question to ask about the files
            file_paths: List of file paths to search
            vector_store_name: Name for the temporary vector store
            max_results: Maximum number of results to return
            delete_after: Whether to delete the vector store after the query
            truncation: Truncation strategy
            
        Returns:
            The API response as a dictionary
        """
        # Prepare the files for upload
        files = {}
        for i, file_path in enumerate(file_paths):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Use the original filename as the key
            filename = os.path.basename(file_path)
            files[f"files"] = (filename, open(file_path, "rb"))
        
        # Prepare the form data
        data = {
            "input_text": query,
            "vector_store_name": vector_store_name,
            "max_results": max_results,
            "delete_after": delete_after,
            "truncation": truncation
        }
        
        try:
            # Make the request
            response = requests.post(self.endpoint, files=files, data=data)
            
            # Close all file handles
            for file_obj in files.values():
                if hasattr(file_obj[1], 'close'):
                    file_obj[1].close()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            # Close all file handles in case of exception
            for file_obj in files.values():
                if hasattr(file_obj[1], 'close'):
                    file_obj[1].close()
            
            raise e

def create_sample_files():
    """
    Create sample files of different types for testing.
    
    Returns:
        A list of file paths to the created sample files
    """
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    # Create a sample text file
    txt_content = """
    # Project Overview
    
    This document provides an overview of the Azure OpenAI integration project.
    
    ## Objectives
    
    1. Implement a RESTful API for Azure OpenAI services
    2. Support text, tool calling, and multimodal inputs
    3. Add file search capabilities for document analysis
    4. Ensure proper error handling and logging
    
    ## Timeline
    
    - Phase 1: Basic API implementation (Weeks 1-2)
    - Phase 2: Tool calling integration (Weeks 3-4)
    - Phase 3: File search capabilities (Weeks 5-6)
    - Phase 4: Testing and documentation (Weeks 7-8)
    
    ## Budget
    
    The estimated budget for this project is $50,000, including:
    - Development costs: $30,000
    - Azure OpenAI API usage: $15,000
    - Contingency: $5,000
    """
    
    txt_path = os.path.join(temp_dir, "project_overview.txt")
    with open(txt_path, "w") as f:
        f.write(txt_content)
    file_paths.append(txt_path)
    
    # Create a sample markdown file
    md_content = """
    # Meeting Minutes: April 1, 2025
    
    ## Attendees
    
    - John Smith (Project Manager)
    - Jane Doe (Lead Developer)
    - Bob Johnson (AI Specialist)
    - Alice Williams (Product Owner)
    
    ## Agenda Items
    
    1. Project status update
    2. Azure OpenAI integration challenges
    3. Next steps and action items
    
    ## Discussion
    
    ### Project Status
    
    The team reported that the project is on track. The basic API implementation is complete, and work has begun on the tool calling integration.
    
    ### Azure OpenAI Integration Challenges
    
    The team discussed several challenges with the Azure OpenAI integration:
    
    - Rate limiting issues when making multiple requests
    - Handling large file uploads for the file search functionality
    - Managing vector store creation and deletion efficiently
    
    ### Next Steps
    
    1. Jane will optimize the rate limiting handling
    2. Bob will implement chunking for large file uploads
    3. Alice will create user stories for the file search UI
    
    ## Action Items
    
    - [ ] Jane: Implement rate limiting solution by April 8
    - [ ] Bob: Create file chunking mechanism by April 10
    - [ ] Alice: Finalize file search UI designs by April 7
    - [ ] John: Schedule follow-up meeting for April 15
    """
    
    md_path = os.path.join(temp_dir, "meeting_minutes.md")
    with open(md_path, "w") as f:
        f.write(md_content)
    file_paths.append(md_path)
    
    # Create a sample JSON file
    json_content = """
    {
      "api_endpoints": {
        "text": {
          "path": "/api/text",
          "method": "POST",
          "description": "Generate text responses from Azure OpenAI"
        },
        "tool_calling": {
          "path": "/api/tool-calling",
          "method": "POST",
          "description": "Use function calling capabilities"
        },
        "text_and_image": {
          "path": "/api/text-and-image",
          "method": "POST",
          "description": "Process multimodal inputs with text and images"
        },
        "file_search": {
          "path": "/api/file-search",
          "method": "POST",
          "description": "Search through uploaded files using vector embeddings"
        }
      },
      "supported_file_types": [
        "pdf",
        "docx",
        "txt",
        "md",
        "json",
        "csv"
      ],
      "version": "1.0.0",
      "last_updated": "2025-04-01"
    }
    """
    
    json_path = os.path.join(temp_dir, "api_documentation.json")
    with open(json_path, "w") as f:
        f.write(json_content)
    file_paths.append(json_path)
    
    return temp_dir, file_paths

def main():
    # Create sample files
    temp_dir, file_paths = create_sample_files()
    print(f"Created sample files in: {temp_dir}")
    for path in file_paths:
        print(f"  - {path}")
    
    try:
        # Initialize the client
        client = FileSearchClient()
        
        # Test queries
        queries = [
            "What is the project timeline?",
            "Who attended the meeting on April 1?",
            "What are the supported file types for the API?",
            "What challenges were discussed in the meeting?",
            "What is the budget for the project?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = client.search(query, file_paths)
            
            if result:
                print(f"Response ID: {result['response_id']}")
                print(f"Output: {result['output']}")
                print(f"Status: {result['status']}")
            
            print("-" * 50)
    
    finally:
        # Clean up
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            print(f"Removed temporary directory: {temp_dir}")

if __name__ == "__main__":
    main()
