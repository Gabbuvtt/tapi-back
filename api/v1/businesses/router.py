"""
Business API endpoints.

POST /businesses        — Register a new business
GET  /businesses/{slug} — Public business info (NFC landing)
PUT  /businesses/{id}   — Update business (owner only)
GET  /businesses/mine   — Get my businesses
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies import (
    get_business_repo,
    get_cache,
    get_current_user_id,
)
from api.v1.businesses.schemas import (
    BusinessCreateRequest,
    BusinessPublicResponse,
    BusinessResponse,
    BusinessUpdateRequest,
)
from core.constants import MemberRole
from core.exceptions import NotFoundError, AlreadyExistsError
from domain.entities.business import Business, BusinessMember
from domain.repositories.business_repository import BusinessRepository
from infraestructure.cache.redis_cache import RedisCache

router = APIRouter()


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=201,
    summary="Register a new business",
    description="Create a new business and assign the current user as the owner.",
)
async def create_business(
    request: BusinessCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    business_repo: BusinessRepository = Depends(get_business_repo),
):
    business = Business(
        name=request.name,
        email=request.email,
        phone=request.phone,
        address=request.address,
        google_place_id=request.google_place_id,
        category=request.category,
        logo_url=request.logo_url,
        owner_id=user_id,
    )

    # Check slug uniqueness
    existing = await business_repo.get_by_slug(business.slug)
    if existing:
        raise AlreadyExistsError(resource="Business", detail="A business with this name already exists")

    business = await business_repo.create(business)

    # Add owner as a member
    member = BusinessMember(
        business_id=business.id,
        user_id=user_id,
        role=MemberRole.OWNER,
    )
    await business_repo.add_member(member)

    return BusinessResponse(
        id=business.id, name=business.name, slug=business.slug,
        email=business.email, phone=business.phone, address=business.address,
        google_place_id=business.google_place_id, logo_url=business.logo_url,
        category=business.category, is_active=business.is_active,
        owner_id=business.owner_id, created_at=business.created_at,
        updated_at=business.updated_at,
    )


@router.get(
    "/mine",
    response_model=list[BusinessResponse],
    summary="Get my businesses",
    description="Retrieve all businesses owned by the current user.",
)
async def get_my_businesses(
    user_id: UUID = Depends(get_current_user_id),
    business_repo: BusinessRepository = Depends(get_business_repo),
):
    businesses = await business_repo.get_by_owner(user_id)
    return [
        BusinessResponse(
            id=b.id, name=b.name, slug=b.slug, email=b.email,
            phone=b.phone, address=b.address, google_place_id=b.google_place_id,
            logo_url=b.logo_url, category=b.category, is_active=b.is_active,
            owner_id=b.owner_id, created_at=b.created_at, updated_at=b.updated_at,
        )
        for b in businesses
    ]


@router.get(
    "/{slug}",
    response_model=BusinessPublicResponse,
    summary="Get public business info",
    description="Retrieve public business information by slug. Used for the NFC scan landing page.",
)
async def get_business_by_slug(
    slug: str,
    business_repo: BusinessRepository = Depends(get_business_repo),
    cache: RedisCache = Depends(get_cache),
):
    # Try cache first
    cached = await cache.get_business(slug)
    if cached:
        return BusinessPublicResponse(**cached)

    business = await business_repo.get_by_slug(slug)
    if not business:
        raise NotFoundError(resource="Business")

    response = BusinessPublicResponse(
        id=business.id, name=business.name, slug=business.slug,
        logo_url=business.logo_url, category=business.category,
        address=business.address, google_place_id=business.google_place_id,
    )

    # Cache for next request
    await cache.set_business(slug, response.model_dump(mode="json"))
    return response


@router.put(
    "/{business_id}",
    response_model=BusinessResponse,
    summary="Update business",
    description="Update business information. Only the owner can update.",
)
async def update_business(
    business_id: UUID,
    request: BusinessUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    business_repo: BusinessRepository = Depends(get_business_repo),
    cache: RedisCache = Depends(get_cache),
):
    business = await business_repo.get_by_id(business_id)
    if not business:
        raise NotFoundError(resource="Business")

    if business.owner_id != user_id:
        from core.exceptions import InsufficientPermissionsError
        raise InsufficientPermissionsError()

    old_slug = business.slug
    business.update(**request.model_dump(exclude_none=True))
    business = await business_repo.update(business)

    # Invalidate cache
    await cache.invalidate_business(old_slug)
    if business.slug != old_slug:
        await cache.invalidate_business(business.slug)

    return BusinessResponse(
        id=business.id, name=business.name, slug=business.slug,
        email=business.email, phone=business.phone, address=business.address,
        google_place_id=business.google_place_id, logo_url=business.logo_url,
        category=business.category, is_active=business.is_active,
        owner_id=business.owner_id, created_at=business.created_at,
        updated_at=business.updated_at,
    )
