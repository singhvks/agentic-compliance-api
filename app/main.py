from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Model-Agnostic Compliance Analysis API demonstrating modern GenAI backend architecture.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(router)

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
