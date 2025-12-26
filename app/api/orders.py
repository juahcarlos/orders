"""Orders API endpoints for create and show order by ID and all orders for certain user."""
import uuid

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.core.dependencies import CurrentUser, get_order_repository
from app.schemas.order_schemas import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.utils.limiter import limiter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_service(
    order_repo=Depends(get_order_repository),
) -> OrderService:
    """Create dependicy from order_repository"""
    return OrderService(order_repo)


@router.post(
    "/",
    dependencies=[Depends(oauth2_scheme)],
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("600/minute")
async def create_order(
    request: Request,
    data: OrderCreate,
    user: CurrentUser,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Create order"""
    order = await service.create_order(
        data=data,
        user_id=user.user_id,
    )
    return order


@router.get(
    "/{order_id}/",
    dependencies=[Depends(oauth2_scheme)],
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
async def get_order(
    order_id: uuid.UUID,
    user: CurrentUser,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Get order by id"""
    order = await service.get_order(order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get(
    "/user/{user_id}",
    dependencies=[Depends(oauth2_scheme)],
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK
)
async def get_order_user(
    user_id: int,
    user: CurrentUser,
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    """Get order by user_id"""
    result = await service.get_order_user(user_id=user_id)
    return result


@router.patch(
    "/{order_id}",
    dependencies=[Depends(oauth2_scheme)],
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit("600/minute")
async def get_order_user(
    request: Request,
    data: OrderCreate,
    order_id: uuid.UUID,
    user: CurrentUser,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Update order"""
    order = await service.patch_order(data=data, order_id=order_id)
    return order



