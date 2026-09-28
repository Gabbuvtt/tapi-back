"""
Loyalty API endpoints.

Programs, cards, rewards, and redemptions.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_current_user_id, get_loyalty_service
from api.v1.loyalty.schemas import (
    LoyaltyCardResponse,
    LoyaltyProgramCreate,
    LoyaltyProgramResponse,
    LoyaltyProgramUpdate,
    RedeemRequest,
    RedemptionResponse,
    RewardCreate,
    RewardResponse,
)
from domain.services.loyalty_service import LoyaltyService

router = APIRouter()


# ── Programs ────────────────────────────────────────────

@router.post(
    "/programs",
    response_model=LoyaltyProgramResponse,
    status_code=201,
    summary="Create loyalty program",
    description="Create a new loyalty program for a business. Only one active program per business.",
)
async def create_program(
    request: LoyaltyProgramCreate,
    business_id: UUID = Query(..., description="Business ID"),
    user_id: UUID = Depends(get_current_user_id),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    program = await loyalty_service.create_program(
        business_id=business_id,
        name=request.name,
        program_type=request.program_type,
        visits_required=request.visits_required,
        points_per_visit=request.points_per_visit,
    )
    return LoyaltyProgramResponse(
        id=program.id, business_id=program.business_id, name=program.name,
        program_type=program.program_type, visits_required=program.visits_required,
        points_per_visit=program.points_per_visit, is_active=program.is_active,
        created_at=program.created_at,
    )


@router.get(
    "/programs/{program_id}",
    response_model=LoyaltyProgramResponse,
    summary="Get loyalty program",
)
async def get_program(
    program_id: UUID,
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    program = await loyalty_service.get_program(program_id)
    return LoyaltyProgramResponse(
        id=program.id, business_id=program.business_id, name=program.name,
        program_type=program.program_type, visits_required=program.visits_required,
        points_per_visit=program.points_per_visit, is_active=program.is_active,
        created_at=program.created_at,
    )


@router.put(
    "/programs/{program_id}",
    response_model=LoyaltyProgramResponse,
    summary="Update loyalty program",
)
async def update_program(
    program_id: UUID,
    request: LoyaltyProgramUpdate,
    user_id: UUID = Depends(get_current_user_id),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    program = await loyalty_service.update_program(
        program_id, **request.model_dump(exclude_none=True)
    )
    return LoyaltyProgramResponse(
        id=program.id, business_id=program.business_id, name=program.name,
        program_type=program.program_type, visits_required=program.visits_required,
        points_per_visit=program.points_per_visit, is_active=program.is_active,
        created_at=program.created_at,
    )


# ── Cards ───────────────────────────────────────────────

@router.get(
    "/cards",
    response_model=list[LoyaltyCardResponse],
    summary="Get my loyalty cards",
    description="Retrieve all loyalty cards for the current user.",
)
async def get_my_cards(
    user_id: UUID = Depends(get_current_user_id),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    cards = await loyalty_service.get_user_cards(user_id)
    return [
        LoyaltyCardResponse(
            id=c.id, program_id=c.program_id, business_id=c.business_id,
            current_visits=c.current_visits, current_points=c.current_points,
            total_visits=c.total_visits, total_points=c.total_points,
            status=c.status, progress_pct=c.progress_pct,
            last_visit_at=c.last_visit_at, created_at=c.created_at,
        )
        for c in cards
    ]


# ── Rewards ─────────────────────────────────────────────

@router.post(
    "/rewards",
    response_model=RewardResponse,
    status_code=201,
    summary="Create a reward",
    description="Create a new reward within a loyalty program.",
)
async def create_reward(
    request: RewardCreate,
    business_id: UUID = Query(..., description="Business ID"),
    user_id: UUID = Depends(get_current_user_id),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    reward = await loyalty_service.create_reward(
        program_id=request.program_id,
        business_id=business_id,
        title=request.title,
        description=request.description,
        reward_type=request.reward_type,
        value=request.value,
        points_cost=request.points_cost,
        visits_cost=request.visits_cost,
        stock=request.stock,
    )
    return RewardResponse(
        id=reward.id, program_id=reward.program_id, business_id=reward.business_id,
        title=reward.title, description=reward.description,
        reward_type=reward.reward_type, value=reward.value,
        points_cost=reward.points_cost, visits_cost=reward.visits_cost,
        stock=reward.stock, is_active=reward.is_active,
    )


@router.get(
    "/rewards",
    response_model=list[RewardResponse],
    summary="List rewards",
    description="List all available rewards for a loyalty program.",
)
async def list_rewards(
    program_id: UUID = Query(..., description="Loyalty program ID"),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    from domain.repositories.loyalty_repository import LoyaltyRepository
    rewards = await loyalty_service._loyalty_repo.get_rewards_by_program(program_id)
    return [
        RewardResponse(
            id=r.id, program_id=r.program_id, business_id=r.business_id,
            title=r.title, description=r.description,
            reward_type=r.reward_type, value=r.value,
            points_cost=r.points_cost, visits_cost=r.visits_cost,
            stock=r.stock, is_active=r.is_active,
        )
        for r in rewards
    ]


# ── Redemptions ─────────────────────────────────────────

@router.post(
    "/redeem",
    response_model=RedemptionResponse,
    status_code=201,
    summary="Redeem a reward",
    description="Redeem a reward and receive a unique code to present at the store.",
)
async def redeem_reward(
    request: RedeemRequest,
    user_id: UUID = Depends(get_current_user_id),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
):
    redemption = await loyalty_service.redeem_reward(
        user_id=user_id,
        reward_id=request.reward_id,
    )
    return RedemptionResponse(
        id=redemption.id, reward_id=redemption.reward_id,
        code=redemption.code, status=redemption.status,
        redeemed_at=redemption.redeemed_at, expires_at=redemption.expires_at,
    )
