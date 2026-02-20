import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel


class ItemIn(BaseModel):
    name: str
    description: str = ""


class ItemOut(ItemIn):
    id: int


app = FastAPI(title="Production CRUD API Template", version="0.1.0")
items: dict[int, ItemOut] = {}
next_id = 1
request_log: dict[str, deque[float]] = defaultdict(deque)


def require_api_key(request: Request) -> None:
    if request.headers.get("X-API-Key") != "dev-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.middleware("http")
async def rate_limit(request: Request, call_next: Callable):
    key = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = request_log[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    bucket.append(now)
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/items", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn, request: Request):
    global next_id
    require_api_key(request)
    item = ItemOut(id=next_id, **payload.model_dump())
    items[next_id] = item
    next_id += 1
    return item


@app.get("/api/v1/items", response_model=list[ItemOut])
def list_items(request: Request, limit: int = 20, offset: int = 0):
    require_api_key(request)
    data = list(items.values())
    return data[offset : offset + limit]


@app.get("/api/v1/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int, request: Request):
    require_api_key(request)
    item = items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.patch("/api/v1/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemIn, request: Request):
    require_api_key(request)
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = ItemOut(id=item_id, **payload.model_dump())
    return items[item_id]


@app.delete("/api/v1/items/{item_id}", status_code=204)
def delete_item(item_id: int, request: Request):
    require_api_key(request)
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return None