from fastapi import APIRouter
from app.schemas.item import Item

router = APIRouter(prefix="/items", tags=["Items"])


# Temporary in-memory store
items_db = []

# GET /items — list items
@router.get("/")
def list_items():
    return items_db


# POST /items — create an item
@router.post("/")
def create_item(item: Item):
    items_db.append(item)
    return {"message": "Item created", "item": item}
