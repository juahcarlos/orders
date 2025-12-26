import time

from celery import Celery

from app.utils.logs import log

celery_app = Celery('tasks', broker='redis://redis:6379/0')

@celery_app.task
def process_order_task(order_data: dict):
    time.sleep(10)
    log.debug(f"DEBUG: process_order_task Order {order_data['id']} processed")
    print(f"DEBUG: process_order_task Order {order_data['id']} processed")
    return order_data['id']
