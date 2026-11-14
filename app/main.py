from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the service process is available."""
    return {"status": "ok"}
