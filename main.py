from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0", "service": "fde-delivery-kit"}
