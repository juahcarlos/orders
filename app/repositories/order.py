import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Order
from app.repositories.base import BaseRepository
from app.schemas.order_schemas import OrderCreate, OrderStatus


class OrderRepository(BaseRepository[Order]):
    """Repository for work with orders"""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Order, session)

    async def create_order(
        self,
        user_id: int,
        items: str,
        total_price: float,
        status: OrderStatus,
    ) -> Order:
        res = await self.create(
            user_id=user_id,
            items=items,
            total_price=total_price,
            status=status.value,
        )
        return res

    async def update_order(
        self,
        order: Order,
        data: OrderCreate,
    ) -> Order:
        res = await self.update(
            order,
            data=data,
        )
        return res

    async def get_order(
        self,
        id: uuid.UUID,
    ) -> Order:
        res = await self.get_by_id(id=id)
        return res

    async def get_order_user(
        self,
        user_id: int,
    ) -> list[Order]:
        res = await self.get_multi(filters={"user_id":user_id})
        return res
