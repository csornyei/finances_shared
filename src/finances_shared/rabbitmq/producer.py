import asyncio
import aio_pika
import json
import datetime
from logging import Logger
from json import JSONEncoder
from finances_shared.params import RabbitMQParams


class DatetimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


class RabbitMQProducer:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self._lock = asyncio.Lock()

    async def connect(self, logger: Logger):
        params = RabbitMQParams.from_env()
        self.connection = await aio_pika.connect_robust(
            params.connection_string(), heartbeat=30
        )

        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name, durable=True)
        logger.info(f"Connected to RabbitMQ on queue: {self.queue_name}")

    async def send_message(self, message: dict, logger: Logger):
        if not self.connection or self.connection.is_closed:
            await self.connect(logger)

        message_json = json.dumps(message, cls=DatetimeEncoder)
        async with self._lock:
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_json.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=self.queue_name,
            )
            logger.info(
                json.dumps(
                    {
                        "message": message_json,
                        "status": "sending",
                        "queue": self.queue_name,
                    }
                )
            )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self.connection = None
            self.channel = None
            print("RabbitMQ connection closed.")
        else:
            print("RabbitMQ connection is already closed or was never opened.")
