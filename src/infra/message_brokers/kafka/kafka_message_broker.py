# from dataclasses import dataclass
# from typing import AsyncIterator
#
#
# from src.infra.message_brokers.base import BaseMessageBroker
# from src.infra.message_brokers.kafka.kafka_consumer import KafkaConsumer
# from src.infra.message_brokers.kafka.kafka_producer import KafkaProducer
#
#
# @dataclass
# class KafkaMessageBroker(BaseMessageBroker):
#     producer: KafkaProducer
#     consumer: KafkaConsumer
#
#     # Implementation of the abstract send_message
#     async def send_message(self, topic: str, key: bytes, value: bytes) -> None:
#         # It calls its producer's send method
#         await self.producer.send(topic=topic, key=key, value=value)
#
#     async def start(self) -> None:
#         if hasattr(self.producer, 'start'): # If BaseProducer had start/stop
#              await self.producer.start()
#         if hasattr(self.consumer, 'start'): # If BaseConsumer had start/stop
#              await self.consumer.start()
#
#     async def stop(self) -> None:
#         # Similar logic for stop
#         pass
#
#     async def start_consuming(self, topic: str) -> AsyncIterator[dict]:
#         await self.consumer.subscribe(topics=[topic])
#         async for msg in self.consumer:
#             yield msg
#
#
#     async def stop_consuming(self, topic: str) -> None: # topic arg might be redundant
#         if hasattr(self.consumer, 'unsubscribe'):
#             await self.consumer.unsubscribe()
#         raise NotImplementedError()