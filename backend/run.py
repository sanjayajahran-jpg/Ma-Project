import uvicorn
import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting EVnesia PRO FastAPI Backend on http://localhost:{port}")
    print(f"Swagger UI Docs: http://localhost:{port}/docs")
    print(f"Admin Dashboard: http://localhost:{port}/admin")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
