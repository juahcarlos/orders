"""Kafka consumer service for order processing."""
import json

from confluent_kafka import Consumer, KafkaError

from app.tasks import process_order_task
from app.utils.logs import log

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'order-processing-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})

consumer.subscribe(['orders'])

def run_consumer():
    """Continuously poll Kafka messages and dispatch 'new_order' events to Celery."""
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            log.debug(f"ConsumerError: {msg.error()}")
            continue

        try:
            data = json.loads(msg.value().decode('utf-8'))
            log.debug(f"ConsumerData: {data}")
            if data.get('event_type') == 'new_order':
                log.debug(f"if event_type == new_order ConsumerData: {data}")
                process_order_task.delay(data['data'])
                consumer.commit(msg)
        except Exception as e:
            log.debug(f"ErrorProcessing_message: {e}")

if __name__ == "__main__":
    log.debug("Starting Kafka consumers ...")
    run_consumer()
