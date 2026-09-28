"""
Menu API endpoints.

POST /menus             — Create a digital menu
GET  /menus/{business_id} — Get the public menu for a business
PUT  /menus/{menu_id}   — Update a menu
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies import get_cache, get_current_user_id, get_menu_repo
from api.v1.menus.schemas import (
    MenuCategorySchema,
    MenuCreateRequest,
    MenuItemSchema,
    MenuResponse,
    MenuUpdateRequest,
)
from core.exceptions import NotFoundError
from domain.entities.menu import Menu, MenuCategory, MenuItem
from domain.repositories.menu_repository import MenuRepository
from infraestructure.cache.redis_cache import RedisCache

router = APIRouter()


def _entity_to_response(menu: Menu) -> MenuResponse:
    """Convert domain Menu entity to API response."""
    return MenuResponse(
        id=menu.id,
        business_id=menu.business_id,
        name=menu.name,
        is_active=menu.is_active,
        categories=[
            MenuCategorySchema(
                name=cat.name,
                order=cat.order,
                items=[
                    MenuItemSchema(
                        name=item.name,
                        description=item.description,
                        price=item.price,
                        currency=item.currency,
                        image_url=item.image_url,
                        is_available=item.is_available,
                        tags=item.tags,
                    )
                    for item in cat.items
                ],
            )
            for cat in menu.categories
        ],
        created_at=menu.created_at,
        updated_at=menu.updated_at,
    )


@router.post(
    "",
    response_model=MenuResponse,
    status_code=201,
    summary="Create a menu",
    description="Create a digital menu for a business.",
)
async def create_menu(
    request: MenuCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    menu_repo: MenuRepository = Depends(get_menu_repo),
):
    menu = Menu(
        business_id=request.business_id,
        name=request.name,
        categories=[
            MenuCategory(
                name=cat.name,
                order=cat.order,
                items=[
                    MenuItem(
                        name=item.name,
                        description=item.description,
                        price=item.price,
                        currency=item.currency,
                        image_url=item.image_url,
                        is_available=item.is_available,
                        tags=item.tags,
                    )
                    for item in cat.items
                ],
            )
            for cat in request.categories
        ],
    )
    menu = await menu_repo.create(menu)
    return _entity_to_response(menu)


@router.get(
    "/{business_id}",
    response_model=MenuResponse,
    summary="Get business menu",
    description="Retrieve the active digital menu for a business. Uses cache for performance.",
)
async def get_menu(
    business_id: UUID,
    menu_repo: MenuRepository = Depends(get_menu_repo),
    cache: RedisCache = Depends(get_cache),
):
    # Try cache first
    cached = await cache.get_menu(str(business_id))
    if cached:
        return MenuResponse(**cached)

    menu = await menu_repo.get_by_business(business_id)
    if not menu:
        raise NotFoundError(resource="Menu")

    response = _entity_to_response(menu)

    # Cache the result
    await cache.set_menu(str(business_id), response.model_dump(mode="json"))
    return response


@router.put(
    "/{menu_id}",
    response_model=MenuResponse,
    summary="Update menu",
    description="Update a menu's name and/or categories.",
)
async def update_menu(
    menu_id: str,
    request: MenuUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    menu_repo: MenuRepository = Depends(get_menu_repo),
    cache: RedisCache = Depends(get_cache),
):
    menu = await menu_repo.get_by_business(UUID(int=0))  # Placeholder
    # Fetch by ID instead
    from infraestructure.database.mongodb.connection import get_mongodb
    from bson import ObjectId

    db = get_mongodb()
    doc = await db["menus"].find_one({"_id": ObjectId(menu_id)})
    if not doc:
        raise NotFoundError(resource="Menu")

    from infraestructure.database.mongodb.repositories.menu_repo import MongoMenuRepository
    repo = MongoMenuRepository(db)

    # Reconstruct entity from doc
    menu = repo._to_entity(doc)

    if request.name:
        menu.name = request.name
    if request.categories is not None:
        menu.categories = [
            MenuCategory(
                name=cat.name,
                order=cat.order,
                items=[
                    MenuItem(
                        name=item.name,
                        description=item.description,
                        price=item.price,
                        currency=item.currency,
                        image_url=item.image_url,
                        is_available=item.is_available,
                        tags=item.tags,
                    )
                    for item in cat.items
                ],
            )
            for cat in request.categories
        ]

    menu = await repo.update(menu)

    # Invalidate cache
    await cache.invalidate_menu(str(menu.business_id))

    return _entity_to_response(menu)
