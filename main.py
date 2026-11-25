from fastapi import FastAPI, Depends
from typing import Annotated

from schemas import Item, SearchQuery, DocMeta,HealthResponse, Echo

app = FastAPI()


async def common_parameters(limit: int = 10):
    return {"word": "Hello World", "limit": limit}

@app.get("/")
async def root(commons: Annotated[dict, Depends(common_parameters)]):
    # return {"message": "Hello World"}
    return commons

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.post("/echo/")
async def echo(echo: Echo) -> Echo:
    return echo


@app.post("/items/search")
async def search_items(query: SearchQuery, meta: DocMeta):
    return {"query": query, "meta": meta}


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}

@app.get("/health", response_model=HealthResponse)
async def health(commons: Annotated[dict, Depends(common_parameters)]):
    return {"status": "ok", "version": "0.1.0", "service": "fde-delivery-kit", **commons}
