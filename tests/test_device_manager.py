"""Tests for Device Manager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from smart_home_brain.core.device_manager import (
    DeviceManager,
    Device,
    DeviceType,
    DeviceCapability,
)


@pytest.fixture
def device_manager():
    """Create device manager instance."""
    return DeviceManager()


@pytest.fixture
def sample_device():
    """Create sample device."""
    return Device(
        id="broadlink_test",
        name="Test Device",
        device_type=DeviceType.BROADLINK_IR,
        ip_address="192.168.1.100",
        mac_address="E8:16:56:00:00:00",
        manufacturer="BroadLink",
        model="RM4PRO",
        capabilities=[
            DeviceCapability.IR_SEND,
            DeviceCapability.IR_LEARN,
        ],
    )


class TestDevice:
    """Tests for Device class."""

    def test_device_to_dict(self, sample_device):
        """Test device serialization."""
        result = sample_device.to_dict()
        
        assert result["id"] == "broadlink_test"
        assert result["name"] == "Test Device"
        assert result["device_type"] == "broadlink_ir"
        assert result["ip_address"] == "192.168.1.100"
        assert "ir_send" in result["capabilities"]


class TestDeviceManager:
    """Tests for DeviceManager class."""

    @pytest.mark.asyncio
    async def test_discover_devices(self, device_manager):
        """Test device discovery."""
        with patch.object(device_manager, '_discover_broadlink', new_callable=AsyncMock):
            with patch.object(device_manager, '_discover_network_devices', new_callable=AsyncMock):
                devices = await device_manager.discover_devices()
                
                assert isinstance(devices, list)

    def test_infer_device_type_broadlink(self, device_manager):
        """Test device type inference for BroadLink."""
        result = device_manager._infer_device_type("BroadLink")
        assert result == DeviceType.BROADLINK_IR

    def test_infer_device_type_amazon(self, device_manager):
        """Test device type inference for Amazon."""
        result = device_manager._infer_device_type("Amazon Technologies")
        assert result == DeviceType.ALEXA_ECHO

    def test_infer_device_type_google(self, device_manager):
        """Test device type inference for Google."""
        result = device_manager._infer_device_type("Google, Inc.")
        assert result == DeviceType.CHROMECAST

    def test_infer_device_type_unknown(self, device_manager):
        """Test device type inference for unknown."""
        result = device_manager._infer_device_type("Some Random Manufacturer")
        assert result == DeviceType.UNKNOWN