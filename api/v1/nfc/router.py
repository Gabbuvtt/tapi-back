"""
NFC API endpoints.

POST /nfc/scan  — Register an NFC scan event
POST /nfc/tags  — Register a new NFC tag (business)
GET  /nfc/tags  — List tags for a business
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies import (
    get_current_user_id,
    get_nfc_repo,
    get_nfc_service,
)
from api.v1.businesses.schemas import BusinessPublicResponse
from api.v1.loyalty.schemas import LoyaltyCardResponse
from api.v1.nfc.schemas import (
    NfcScanRequest,
    NfcScanResponse,
    NfcTagCreate,
    NfcTagResponse,
)
from domain.entities.nfc_scan import NfcTag
from domain.repositories.nfc_repository import NfcRepository
from domain.services.nfc_service import NfcService

router = APIRouter()


@router.post(
    "/scan",
    response_model=NfcScanResponse,
    summary="Register NFC scan",
    description=(
        "Register an NFC scan event. Automatically updates the user's "
        "loyalty card and returns business info with loyalty progress."
    ),
)
async def register_scan(
    body: NfcScanRequest,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    nfc_service: NfcService = Depends(get_nfc_service),
):
    result = await nfc_service.register_scan(
        tag_uid=body.tag_uid,
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    business = result["business"]
    loyalty = result["loyalty"]

    # Build loyalty card response if active
    loyalty_card = None
    if loyalty.get("loyalty_active") and loyalty.get("card"):
        card = loyalty["card"]
        program = loyalty["program"]
        loyalty_card = LoyaltyCardResponse(
            id=card.id,
            program_id=card.program_id,
            business_id=card.business_id,
            current_visits=card.current_visits,
            current_points=card.current_points,
            total_visits=card.total_visits,
            total_points=card.total_points,
            status=card.status,
            progress_pct=loyalty.get("progress_pct", 0.0),
            last_visit_at=card.last_visit_at,
            created_at=card.created_at,
        )

    return NfcScanResponse(
        business=BusinessPublicResponse(
            id=business.id, name=business.name, slug=business.slug,
            logo_url=business.logo_url, category=business.category,
            address=business.address, google_place_id=business.google_place_id,
        ),
        loyalty_card=loyalty_card,
        scan_count=result["scan_count"],
        message=loyalty.get("message", f"¡Bienvenido a {business.name}!"),
    )


@router.post(
    "/tags",
    response_model=NfcTagResponse,
    status_code=201,
    summary="Register NFC tag",
    description="Register a new NFC tag and link it to a business.",
)
async def create_tag(
    request: NfcTagCreate,
    user_id: UUID = Depends(get_current_user_id),
    nfc_repo: NfcRepository = Depends(get_nfc_repo),
):
    tag = NfcTag(
        tag_uid=request.tag_uid,
        business_id=request.business_id,
        label=request.label,
    )
    tag = await nfc_repo.create_tag(tag)
    return NfcTagResponse(
        id=tag.id, tag_uid=tag.tag_uid, business_id=tag.business_id,
        label=tag.label, is_active=tag.is_active, created_at=tag.created_at,
    )


@router.get(
    "/tags",
    response_model=list[NfcTagResponse],
    summary="List NFC tags",
    description="List all NFC tags for a business.",
)
async def list_tags(
    business_id: UUID = Query(..., description="Business ID"),
    user_id: UUID = Depends(get_current_user_id),
    nfc_repo: NfcRepository = Depends(get_nfc_repo),
):
    tags = await nfc_repo.get_tags_by_business(business_id)
    return [
        NfcTagResponse(
            id=t.id, tag_uid=t.tag_uid, business_id=t.business_id,
            label=t.label, is_active=t.is_active, created_at=t.created_at,
        )
        for t in tags
    ]
