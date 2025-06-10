# from dataclasses import dataclass
# from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
# from typing import AsyncIterator, Any
#
# from src.infra.message_brokers.base import BaseProducer
#
# @dataclass
# class KafkaProducer(BaseProducer):
#     aio_producer: AIOKafkaProducer
#
#     async def start(self) -> None:
#         await self.aio_producer.start()
#
#     async def stop(self) -> None:
#         await self.aio_producer.stop()
#
#     async def send(self, **kwargs) -> None:
#         # We need to ensure kwargs contain topic, value, and optionally key
#         # This is where a more specific signature in BaseProducer would be safer,
#         # but we can make it work.
#         topic = kwargs.get("topic")
#         value = kwargs.get("value")
#         key = kwargs.get("key", None)
#
#         if topic is None or value is None:
#             raise ValueError("Topic and value must be provided in kwargs for sending message")
#
#         await self.aio_producer.send(topic=topic, value=value, key=key)
#         # For similarity with your first example, you might use send()
#         # If you need confirmation, AIOKafkaProducer also has send_and_wait()
