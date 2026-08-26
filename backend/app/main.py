from fastapi import FastAPI

app = FastAPI(
    title="AegisAI",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "aegis-ai",
    }