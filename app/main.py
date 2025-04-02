from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.routes.responses import router as responses_router

# Create FastAPI app
app = FastAPI(
    title="Azure OpenAI Responses API",
    description="A simple API for interacting with Azure OpenAI Responses API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add GZip middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(responses_router, prefix="/api", tags=["responses"])

# Update the root endpoint to include the new file-search endpoint
@app.get("/")
async def root():
    return {
        "message": "Azure OpenAI Responses API",
        "docs": "/docs",
        "endpoints": [
            "/api/text",
            "/api/tool-calling",
            "/api/text-and-image",
            "/api/file-search"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        # Increase limits for file uploads
        limit_concurrency=10,
        limit_max_requests=100,
        timeout_keep_alive=120
    )
