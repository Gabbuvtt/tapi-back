"""
Menu repository — MongoDB implementation.
"""

from datetime import datetime, timezone
from uuid import UUID

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.entities.menu import Menu, MenuCategory, MenuItem
from domain.repositories.menu_repository import MenuRepository


class MongoMenuRepository(MenuRepository):
    """Concrete menu repository backed by MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["menus"]

    # ── Mappers ─────────────────────────────────────────

    @staticmethod
    def _to_document(menu: Menu) -> dict:
        return {
            "business_id": str(menu.business_id),
            "name": menu.name,
            "is_active": menu.is_active,
            "categories": [
                {
                    "name": cat.name,
                    "order": cat.order,
                    "items": [
                        {
                            "name": item.name,
                            "description": item.description,
                            "price": item.price,
                            "currency": item.currency,
                            "image_url": item.image_url,
                            "is_available": item.is_available,
                            "tags": item.tags,
                        }
                        for item in cat.items
                    ],
                }
                for cat in menu.categories
            ],
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
        }

    @staticmethod
    def _to_entity(doc: dict) -> Menu:
        categories = []
        for cat_doc in doc.get("categories", []):
            items = [
                MenuItem(
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    price=item.get("price", 0.0),
                    currency=item.get("currency", "USD"),
                    image_url=item.get("image_url"),
                    is_available=item.get("is_available", True),
                    tags=item.get("tags", []),
                )
                for item in cat_doc.get("items", [])
            ]
            categories.append(
                MenuCategory(
                    name=cat_doc.get("name", ""),
                    order=cat_doc.get("order", 0),
                    items=items,
                )
            )

        return Menu(
            id=str(doc["_id"]),
            business_id=UUID(doc["business_id"]),
            name=doc.get("name", ""),
            is_active=doc.get("is_active", True),
            categories=categories,
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
        )

    # ── CRUD ────────────────────────────────────────────

    async def create(self, menu: Menu) -> Menu:
        doc = self._to_document(menu)
        result = await self._collection.insert_one(doc)
        menu.id = str(result.inserted_id)
        return menu

    async def get_by_business(self, business_id: UUID) -> Menu | None:
        doc = await self._collection.find_one(
            {"business_id": str(business_id), "is_active": True}
        )
        return self._to_entity(doc) if doc else None

    async def update(self, menu: Menu) -> Menu:
        menu.updated_at = datetime.now(timezone.utc)
        doc = self._to_document(menu)
        await self._collection.replace_one(
            {"_id": ObjectId(menu.id)},
            doc,
        )
        return menu

    async def delete(self, menu_id: str) -> None:
        await self._collection.delete_one({"_id": ObjectId(menu_id)})
