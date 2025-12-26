"""Kafka producer manager for asynchronous message publishing."""
import asyncio
import json

from aiokafka import AIOKafkaProducer


class KafkaManager:
    _producer = None

    @classmethod
    async def start(cls):
        """Initialize and start the Kafka producer with a retry loop."""
        if cls._producer is None:
            cls._producer = AIOKafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            # Retry connection until successful
            while True:
                try:
                    await cls._producer.start()
                    break
                except Exception:
                    await asyncio.sleep(2)

    @classmethod
    async def stop(cls):
        """Gracefully shut down the Kafka producer."""
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None

    @classmethod
    async def send(cls, topic, data):
        """Send a message to a specific topic and wait for confirmation."""
        if cls._producer is None:
            await cls.start()
        await cls._producer.send_and_wait(topic, data)

send_to_kafka = KafkaManager.send
