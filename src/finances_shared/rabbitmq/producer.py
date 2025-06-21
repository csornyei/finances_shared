import asyncio
import datetime
import json
from json import JSONEncoder
from logging import Logger

import aio_pika

from finances_shared.params import RabbitMQParams


class DatetimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


class RabbitMQProducer:
    """
    RabbitMQ Producer for sending messages to a specified queue.
    This class handles connection management, message serialization, and sending messages
    to RabbitMQ using aio_pika for asynchronous operations.

    Usage:
    ```python
    from contextlib import asynccontextmanager
    from finances_shared.rabbitmq.producer import RabbitMQProducer

    producer = RabbitMQProducer("your_queue_name")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            await producer.connect(logger)
            yield
        finally:
            await producer.close()

    app = FastAPI(lifespan=lifespan)

    @app.post("/send_message")
    async def send_message(message: dict):
        await producer.send_message(message, logger)
        return {"status": "Message sent"}
    ```
    """

    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self._lock = asyncio.Lock()

    async def connect(self, params: RabbitMQParams, logger: Logger):
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
