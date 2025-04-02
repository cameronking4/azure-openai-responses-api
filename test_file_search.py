import requests
import os
import tempfile

# Create a temporary test file
def create_test_file(content, filename="test_document.txt"):
    """Create a temporary test file with the given content."""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "w") as f:
        f.write(content)
    
    return file_path

# Test the file search endpoint
def test_file_search(file_path, query):
    """Test the file search endpoint with the given file and query."""
    url = "http://localhost:8000/api/file-search"
    
    # Open the file for upload
    with open(file_path, "rb") as f:
        # Create the form data
        files = {"files": (os.path.basename(file_path), f)}
        data = {
            "input_text": query,
            "vector_store_name": "Test Vector Store",
            "max_results": 10,
            "delete_after": True,
            "truncation": "auto"
        }
        
        # Make the request
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

def main():
    # Sample content for the test file
    content = """
    # Company Values
    
    At Acme Corporation, we believe in the following core values:
    
    1. **Innovation**: We constantly seek new and better ways to serve our customers.
    2. **Integrity**: We are honest, transparent, and ethical in all our dealings.
    3. **Collaboration**: We work together across teams to achieve our common goals.
    4. **Excellence**: We strive for the highest quality in everything we do.
    5. **Customer Focus**: We put our customers at the center of all our decisions.
    
    These values guide our daily actions and long-term strategy. They define who we are as a company and what we stand for.
    
    # Employee Benefits
    
    Acme Corporation offers a comprehensive benefits package including:
    
    - Health, dental, and vision insurance
    - 401(k) retirement plan with company matching
    - Flexible work arrangements
    - Professional development opportunities
    - Paid time off and holidays
    - Parental leave
    - Wellness programs
    
    # Code of Conduct
    
    All employees are expected to:
    
    - Treat others with respect and dignity
    - Maintain confidentiality of company information
    - Avoid conflicts of interest
    - Comply with all applicable laws and regulations
    - Report any violations or concerns
    """
    
    # Create the test file
    file_path = create_test_file(content, "employee_handbook.txt")
    print(f"Created test file: {file_path}")
    
    try:
        # Test queries
        queries = [
            "What are the company values?",
            "Tell me about employee benefits.",
            "What does the code of conduct say?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = test_file_search(file_path, query)
            
            if result:
                print(f"Response ID: {result['response_id']}")
                print(f"Output: {result['output']}")
                print(f"Status: {result['status']}")
            
            print("-" * 50)
    
    finally:
        # Clean up the test file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed test file: {file_path}")

if __name__ == "__main__":
    main()
