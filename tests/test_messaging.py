"""
Tests for RabbitMQ Messaging Manager
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from smart_home_brain.core.messaging import (
    MessagingManager,
    SmartHomeEvent,
    EventType,
    get_messaging,
    close_messaging,
)


def test_event_type_enum():
    """Test EventType enum values."""
    assert EventType.DEVICE_DISCOVERED == "device.discovered"
    assert EventType.DEVICE_STATE_CHANGED == "device.state_changed"
    assert EventType.DEVICE_COMMAND_SENT == "device.command_sent"
    assert EventType.DEVICE_ERROR == "device.error"
    assert EventType.PATTERN_DETECTED == "pattern.detected"
    assert EventType.ANOMALY_DETECTED == "anomaly.detected"
    assert EventType.AUTOMATION_TRIGGERED == "automation.triggered"
    assert EventType.USER_COMMAND == "user.command"


def test_smart_home_event_creation():
    """Test SmartHomeEvent creation."""
    event = SmartHomeEvent(
        event_type=EventType.DEVICE_STATE_CHANGED,
        payload={"device_id": "test_1", "state": {"power": "on"}},
    )
    
    assert event.event_type == EventType.DEVICE_STATE_CHANGED
    assert event.payload["device_id"] == "test_1"
    assert event.source == "smart_home_brain"
    assert event.timestamp is not None
    assert event.correlation_id is None


def test_smart_home_event_serialization():
    """Test SmartHomeEvent JSON serialization."""
    event = SmartHomeEvent(
        event_type=EventType.DEVICE_COMMAND_SENT,
        payload={"device_id": "test_1", "command": "turn_on"},
        correlation_id="corr-123",
    )
    
    json_str = event.to_json()
    assert "device.command_sent" in json_str
    assert "test_1" in json_str
    assert "turn_on" in json_str
    assert "corr-123" in json_str


def test_smart_home_event_deserialization():
    """Test SmartHomeEvent JSON deserialization."""
    json_str = '''{
        "event_type": "device.state_changed",
        "payload": {"device_id": "test_1", "state": {"power": "off"}},
        "timestamp": "2024-01-01T00:00:00",
        "source": "smart_home_brain",
        "correlation_id": null
    }'''
    
    event = SmartHomeEvent.from_json(json_str)
    
    assert event.event_type == EventType.DEVICE_STATE_CHANGED
    assert event.payload["device_id"] == "test_1"
    assert event.payload["state"]["power"] == "off"
    assert event.correlation_id is None


@pytest.mark.asyncio
async def test_messaging_manager_connect_success():
    """Test successful RabbitMQ connection."""
    messaging = MessagingManager(url="amqp://test:test@localhost/")
    
    with patch("aio_pika.connect_robust") as mock_connect:
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        mock_connect.return_value = mock_connection
        
        # Mock exchange declaration
        mock_exchange = AsyncMock()
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        
        result = await messaging.connect()
        
        assert result is True
        assert messaging.is_connected is True
        mock_connect.assert_called_once_with("amqp://test:test@localhost/")


@pytest.mark.asyncio
async def test_messaging_manager_connect_failure():
    """Test RabbitMQ connection failure."""
    messaging = MessagingManager(url="amqp://invalid:invalid@invalid/")
    
    with patch("aio_pika.connect_robust") as mock_connect:
        mock_connect.side_effect = Exception("Connection failed")
        
        result = await messaging.connect()
        
        assert result is False
        assert messaging.is_connected is False


@pytest.mark.asyncio
async def test_publish_event():
    """Test publishing event to RabbitMQ."""
    messaging = MessagingManager()
    messaging._connected = True
    messaging.channel = AsyncMock()
    
    mock_exchange = AsyncMock()
    messaging._exchanges["events"] = mock_exchange
    
    event = SmartHomeEvent(
        event_type=EventType.DEVICE_DISCOVERED,
        payload={"device_id": "test_1"},
    )
    
    with patch("smart_home_brain.core.messaging.Message") as mock_message:
        mock_msg = MagicMock()
        mock_message.return_value = mock_msg
        
        result = await messaging.publish(event)
        
        assert result is True
        mock_exchange.publish.assert_called_once()


@pytest.mark.asyncio
async def test_emit_device_state():
    """Test emitting device state change."""
    messaging = MessagingManager()
    messaging._connected = True
    messaging.channel = AsyncMock()
    messaging.publish = AsyncMock(return_value=True)
    
    await messaging.emit_device_state(
        device_id="device_1",
        state={"power": "on"},
        previous_state={"power": "off"},
    )
    
    messaging.publish.assert_called_once()
    call_args = messaging.publish.call_args
    event = call_args[0][0]
    
    assert event.event_type == EventType.DEVICE_STATE_CHANGED
    assert event.payload["device_id"] == "device_1"
    assert event.payload["state"]["power"] == "on"


@pytest.mark.asyncio
async def test_emit_pattern_detected():
    """Test emitting pattern detected event."""
    messaging = MessagingManager()
    messaging._connected = True
    messaging.publish = AsyncMock(return_value=True)
    
    await messaging.emit_pattern_detected(
        pattern_id="pattern_1",
        pattern_data={"type": "daily", "confidence": 0.95},
    )
    
    messaging.publish.assert_called_once()
    call_args = messaging.publish.call_args
    event = call_args[0][0]
    
    assert event.event_type == EventType.PATTERN_DETECTED
    assert event.payload["pattern_id"] == "pattern_1"


@pytest.mark.asyncio
async def test_emit_anomaly():
    """Test emitting anomaly event."""
    messaging = MessagingManager()
    messaging._connected = True
    messaging.publish = AsyncMock(return_value=True)
    
    await messaging.emit_anomaly(
        anomaly_type="unknown_device",
        severity="high",
        details={"device": "unauthorized_device"},
    )
    
    messaging.publish.assert_called_once()
    call_args = messaging.publish.call_args
    event = call_args[0][0]
    
    assert event.event_type == EventType.ANOMALY_DETECTED
    assert event.payload["anomaly_type"] == "unknown_device"
    assert event.payload["severity"] == "high"


@pytest.mark.asyncio
async def test_send_command():
    """Test sending device command via messaging."""
    messaging = MessagingManager()
    messaging._connected = True
    messaging.publish = AsyncMock(return_value=True)
    
    result = await messaging.send_command(
        device_id="device_1",
        command="turn_on",
        params={"brightness": 100},
    )
    
    assert result is True
    messaging.publish.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup():
    """Test RabbitMQ cleanup."""
    messaging = MessagingManager()
    messaging._connected = True
    messaging.connection = AsyncMock()
    messaging.connection.close = AsyncMock()
    
    await messaging.cleanup()
    
    messaging.connection.close.assert_called_once()
    assert messaging.is_connected is False


@pytest.mark.asyncio
async def test_get_messaging_singleton():
    """Test get_messaging singleton."""
    import os
    original_url = os.environ.get("RABBITMQ_URL")
    
    with patch("smart_home_brain.core.messaging.MessagingManager.connect") as mock_connect:
        mock_connect.return_value = True
        
        messaging1 = await get_messaging()
        messaging2 = await get_messaging()
        
        assert messaging1 is messaging2
    
    # Cleanup
    await close_messaging()
    
    if original_url:
        os.environ["RABBITMQ_URL"] = original_url