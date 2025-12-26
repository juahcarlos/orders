import uuid

from fastapi import HTTPException

from app.core.redis_init import rdb
from app.kafka.kafka_client import send_to_kafka
from app.repositories.order import OrderRepository
from app.schemas.order_schemas import OrderCreate, OrderResponse
from app.utils.logs import log


class OrderService:
    """Service for working with orders."""
    def __init__(self, order_repo: OrderRepository) -> None:
        self.order_repo = order_repo

    async def create_order(
        self,
        data: OrderCreate,
        user_id: int,
    ) -> OrderResponse:
        """Create new order"""
        order = await self.order_repo.create_order(
            user_id=user_id,
            items=data.items,
            total_price=data.total_price,
            status=data.status,
        )

        res = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            created_at=order.created_at,
            total_price=order.total_price,
            items=order.items,
            status=order.status,
        )

        """Send task to Kafka queue"""
        try:
            await send_to_kafka("orders", {
                "event_type": "new_order",
                "data": {"id": order.id, "status": "pending"}
            })
            log.debug(f"DEBUG:  send_new_order_event to QUEUE {order}")
        except Exception as ex:
            log.error(f"ERROR: can't send_new_order_event to QUEUE {order} ex {ex}")

        return OrderResponse.model_validate(res)

    async def patch_order(
        self,
        order_id: uuid.UUID,
        data: OrderCreate,
    ) -> OrderResponse:
        """Update order"""
        order = await self.order_repo.get_order(id=order_id)

        if not order:
            raise HTTPException(404, "Order not found")

        try:
            order_res = await self.order_repo.update_order(
                order,
                data,
            )
        except Exception as ex:
            log.error(f"order_service Order.patch_order ex {ex}")

        res = OrderResponse(
            id=order_res.id,
            user_id=order_res.user_id,
            created_at=order_res.created_at,
            total_price=order_res.total_price,
            items=order_res.items,
            status=order_res.status,
        )
        result = OrderResponse.model_validate(res)

        await rdb.set(f"order:{order_id}", result.model_dump_json(), ex=300)

        return result

    async def get_order(
        self,
        order_id: uuid.UUID,
    ) -> OrderResponse:
        """Get order by ID"""
        if cached := await rdb.get(f"order:{order_id}"):
            return OrderResponse.model_validate_json(cached)

        order = await self.order_repo.get_order(id=order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Use model_validate directly
        res = OrderResponse.model_validate(order)

        await rdb.set(f"order:{order_id}", res.model_dump_json(), ex=300)

        return res

    async def get_order_user(
        self,
        user_id: int,
    ) -> list[OrderResponse]:
        """Get order by user_id"""
        orders = await self.order_repo.get_order_user(user_id=user_id)

        if not orders or len(orders) == 0:
            raise HTTPException(status_code=404, detail=f"No orders for user {user_id}")

        res = [
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                created_at=order.created_at,
                total_price=order.total_price,
                items=order.items,
                status=order.status,
            )
            for order in orders
        ]

        log.info(f"--------- get_order Order.get_order_user res {res}")

        return res
