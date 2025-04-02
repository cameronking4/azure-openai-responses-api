#!/usr/bin/env python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        # Increase limits for file uploads
        limit_concurrency=10,
        limit_max_requests=100,
        timeout_keep_alive=120,
        # Set a larger request body limit (100MB)
        http="httptools",
        ws="websockets",
        loop="asyncio"
    )
