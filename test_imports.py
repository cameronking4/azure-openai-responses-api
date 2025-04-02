try:
    from fastapi import FastAPI
    print("FastAPI imported successfully")
except ImportError as e:
    print(f"Error importing FastAPI: {e}")

try:
    from openai import AzureOpenAI
    print("AzureOpenAI imported successfully")
except ImportError as e:
    print(f"Error importing AzureOpenAI: {e}")

try:
    import uvicorn
    print("uvicorn imported successfully")
except ImportError as e:
    print(f"Error importing uvicorn: {e}")
