"""
RabbitMQ Messaging - Event-driven communication for Smart Home
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

import aio_pika
from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for smart home events."""
    DEVICE_DISCOVERED = "device.discovered"
    DEVICE_STATE_CHANGED = "device.state_changed"
    DEVICE_COMMAND_SENT = "device.command_sent"
    DEVICE_ERROR = "device.error"
    PATTERN_DETECTED = "pattern.detected"
    ANOMALY_DETECTED = "anomaly.detected"
    AUTOMATION_TRIGGERED = "automation.triggered"
    USER_COMMAND = "user.command"


@dataclass
class SmartHomeEvent:
    """Represents a smart home event."""
    event_type: EventType
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str = "smart_home_brain"
    correlation_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps({
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
            "correlation_id": self.correlation_id,
        })
    
    @classmethod
    def from_json(cls, data: str) -> "SmartHomeEvent":
        """Deserialize event from JSON."""
        obj = json.loads(data)
        return cls(
            event_type=EventType(obj["event_type"]),
            payload=obj["payload"],
            timestamp=obj["timestamp"],
            source=obj["source"],
            correlation_id=obj.get("correlation_id"),
        )


class MessagingManager:
    """Manages RabbitMQ connections and message handling."""
    
    def __init__(self, url: str = "amqp://guest:guest@localhost/"):
        self.url = url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.RobustChannel] = None
        self._exchanges: dict[str, aio_pika.RobustExchange] = {}
        self._queues: dict[str, aio_pika.RobustQueue] = {}
        self._subscribers: dict[EventType, list[Callable]] = {}
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect to RabbitMQ."""
        try:
            logger.info(f"🔌 Connecting to RabbitMQ at {self.url}...")
            
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            
            # Set prefetch count
            await self.channel.set_qos(prefetch_count=10)
            
            # Declare exchanges
            await self._declare_exchanges()
            
            self._connected = True
            logger.info("✅ Connected to RabbitMQ")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            self._connected = False
            return False
    
    async def _declare_exchanges(self):
        """Declare exchanges for different event types."""
        if not self.channel:
            return
        
        # Main exchange for all smart home events
        self._exchanges["events"] = await self.channel.declare_exchange(
            "smart_home.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        
        # Exchange for device commands
        self._exchanges["commands"] = await self.channel.declare_exchange(
            "smart_home.commands",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        
        # Exchange for automation
        self._exchanges["automation"] = await self.channel.declare_exchange(
            "smart_home.automation",
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )
    
    async def publish(
        self,
        event: SmartHomeEvent,
        exchange_name: str = "events",
        routing_key: Optional[str] = None,
    ) -> bool:
        """Publish an event to RabbitMQ."""
        if not self._connected or not self.channel:
            logger.warning("RabbitMQ not connected, cannot publish event")
            return False
        
        try:
            exchange = self._exchanges.get(exchange_name)
            if not exchange:
                logger.error(f"Exchange {exchange_name} not found")
                return False
            
            # Default routing key from event type
            if not routing_key:
                routing_key = event.event_type.value
            
            # Create message
            message = Message(
                body=event.to_json().encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                correlation_id=event.correlation_id,
                timestamp=datetime.utcnow(),
            )
            
            # Publish
            await exchange.publish(message, routing_key=routing_key)
            logger.debug(f"Published event: {event.event_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    async def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[SmartHomeEvent], Any],
        queue_name: Optional[str] = None,
    ):
        """Subscribe to events of a specific type."""
        if not self._connected or not self.channel:
            logger.warning("RabbitMQ not connected, cannot subscribe")
            return
        
        # Create queue
        if not queue_name:
            queue_name = f"smart_home.{event_type.value}"
        
        if queue_name not in self._queues:
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True,
            )
            
            # Bind to exchange
            await queue.bind(
                self._exchanges["events"],
                routing_key=event_type.value,
            )
            
            self._queues[queue_name] = queue
        
        # Store handler
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        
        # Start consuming
        async def process_message(message: AbstractIncomingMessage):
            async with message.process():
                try:
                    event = SmartHomeEvent.from_json(message.body.decode())
                    for handler_fn in self._subscribers.get(event_type, []):
                        if asyncio.iscoroutinefunction(handler_fn):
                            await handler_fn(event)
                        else:
                            handler_fn(event)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        await self._queues[queue_name].consume(process_message)
        logger.info(f"Subscribed to {event_type.value} events")
    
    async def send_command(
        self,
        device_id: str,
        command: str,
        params: Optional[dict] = None,
    ) -> bool:
        """Send device command via messaging."""
        event = SmartHomeEvent(
            event_type=EventType.DEVICE_COMMAND_SENT,
            payload={
                "device_id": device_id,
                "command": command,
                "params": params or {},
            },
        )
        return await self.publish(
            event,
            exchange_name="commands",
            routing_key=device_id,
        )
    
    async def emit_device_state(
        self,
        device_id: str,
        state: dict[str, Any],
        previous_state: Optional[dict] = None,
    ):
        """Emit device state changed event."""
        event = SmartHomeEvent(
            event_type=EventType.DEVICE_STATE_CHANGED,
            payload={
                "device_id": device_id,
                "state": state,
                "previous_state": previous_state,
            },
        )
        await self.publish(event)
    
    async def emit_pattern_detected(
        self,
        pattern_id: str,
        pattern_data: dict[str, Any],
    ):
        """Emit pattern detected event."""
        event = SmartHomeEvent(
            event_type=EventType.PATTERN_DETECTED,
            payload={
                "pattern_id": pattern_id,
                **pattern_data,
            },
        )
        await self.publish(event)
    
    async def emit_anomaly(
        self,
        anomaly_type: str,
        severity: str,
        details: dict[str, Any],
    ):
        """Emit anomaly detected event."""
        event = SmartHomeEvent(
            event_type=EventType.ANOMALY_DETECTED,
            payload={
                "anomaly_type": anomaly_type,
                "severity": severity,
                "details": details,
            },
        )
        await self.publish(event)
    
    async def emit_automation_triggered(
        self,
        automation_name: str,
        trigger: str,
        actions: list[dict],
    ):
        """Emit automation triggered event."""
        event = SmartHomeEvent(
            event_type=EventType.AUTOMATION_TRIGGERED,
            payload={
                "automation_name": automation_name,
                "trigger": trigger,
                "actions": actions,
            },
        )
        await self.publish(event, exchange_name="automation")
    
    async def cleanup(self):
        """Cleanup RabbitMQ connection."""
        logger.info("Closing RabbitMQ connection...")
        if self.connection:
            await self.connection.close()
        self._connected = False
        logger.info("✅ RabbitMQ connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to RabbitMQ."""
        return self._connected


# Singleton instance
_messaging_instance: Optional[MessagingManager] = None


async def get_messaging() -> MessagingManager:
    """Get or create messaging instance."""
    global _messaging_instance
    if _messaging_instance is None:
        import os
        url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        _messaging_instance = MessagingManager(url)
        await _messaging_instance.connect()
    return _messaging_instance


async def close_messaging():
    """Close messaging instance."""
    global _messaging_instance
    if _messaging_instance:
        await _messaging_instance.cleanup()
        _messaging_instance = None