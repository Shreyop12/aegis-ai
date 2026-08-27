from fastapi import FastAPI

from backend.app.api.traces import router as traces_router

app = FastAPI(
    title="AegisAI",
    version="0.1.0",
)

app.include_router(traces_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "aegis-ai",
    }