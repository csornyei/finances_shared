import asyncio
import aio_pika

from finances_shared.params import RabbitMQParams
from logging import Logger


class RabbitMQListener:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    async def connect(self, params: RabbitMQParams, logger: Logger):
        self.connection = await aio_pika.connect_robust(
            params.connection_string(), heartbeat=30
        )

        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name, durable=True)
        logger.info(f"Connected to RabbitMQ on queue: {self.queue_name}")

    async def listen(self, callback, logger: Logger):
        if not self.connection or self.connection.is_closed:
            await self.connect(logger)

        queue = await self.channel.get_queue(self.queue_name)

        logger.info(f"Listening for messages on queue: {self.queue_name}")
        await queue.consume(callback)

        await asyncio.Future()  # Keep the listener running
