# from dataclasses import dataclass
# from typing import Any, AsyncIterator
#
# from aiokafka import AIOKafkaConsumer
#
# from src.infra.message_brokers.base import BaseConsumer
# import orjson
#
#
# @dataclass
# class KafkaConsumer(BaseConsumer):
#     aio_consumer: AIOKafkaConsumer
#
#     async def start(self) -> None:
#         await self.aio_consumer.start()
#
#     async def stop(self) -> None:
#         await self.aio_consumer.stop()
#
#     async def subscribe(self, **kwargs) -> None:
#         topics = kwargs.get("topics")
#         if not topics:
#             raise ValueError("You must provide 'topics' in kwargs to subscribe")
#         self.aio_consumer.subscribe(topics=topics)
#
#     async def __aiter__(self) -> AsyncIterator[Any]:
#         async for msg in self.aio_consumer:
#             yield orjson.loads(msg.value)
#
#     async def unsubscribe(self) -> None:
#         await self.aio_consumer.unsubscribe()
