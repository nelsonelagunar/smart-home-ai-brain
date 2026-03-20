"""
Device Manager - Handles discovery and control of smart home devices
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DeviceType(str, Enum):
    """Supported device types."""
    BROADLINK_IR = "broadlink_ir"
    BROADLINK_RF = "broadlink_rf"
    BROADLINK_SENSOR = "broadlink_sensor"
    ALEXA_ECHO = "alexa_echo"
    TUYA_DEVICE = "tuya_device"
    CHROMECAST = "chromecast"
    MIDEA_AC = "midea_ac"
    UNKNOWN = "unknown"


class DeviceCapability(str, Enum):
    """Device capabilities."""
    IR_SEND = "ir_send"
    IR_LEARN = "ir_learn"
    RF_SEND = "rf_send"
    RF_LEARN = "rf_learn"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    VOICE = "voice"
    SMART_HOME = "smart_home"


@dataclass
class Device:
    """Represents a smart home device."""
    id: str
    name: str
    device_type: DeviceType
    ip_address: str
    mac_address: str
    manufacturer: str
    model: Optional[str] = None
    capabilities: list[DeviceCapability] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "device_type": self.device_type.value,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "capabilities": [c.value for c in self.capabilities],
            "state": self.state,
            "last_seen": self.last_seen,
        }


class DeviceManager:
    """Manages smart home devices."""
    
    def __init__(self):
        self.devices: dict[str, Device] = {}
        self._broadlink_devices: dict = {}
        
    async def discover_devices(self) -> list[Device]:
        """Discover all devices on the network."""
        logger.info("🔍 Starting device discovery...")
        
        # Discover BroadLink devices
        await self._discover_broadlink()
        
        # Discover network devices via ARP
        await self._discover_network_devices()
        
        return list(self.devices.values())
    
    async def _discover_broadlink(self):
        """Discover BroadLink devices."""
        try:
            import broadlink
            
            logger.info("📡 Scanning for BroadLink devices...")
            devices = broadlink.discover(timeout=5)
            
            for device in devices:
                dev = self._create_broadlink_device(device)
                if dev:
                    self.devices[dev.id] = dev
                    logger.info(f"✅ Found BroadLink: {dev.name} @ {dev.ip_address}")
                    
        except ImportError:
            logger.warning("⚠️ broadlink library not installed")
        except Exception as e:
            logger.error(f"❌ Error discovering BroadLink devices: {e}")
    
    def _create_broadlink_device(self, broadlink_dev) -> Optional[Device]:
        """Create Device from BroadLink device."""
        try:
            # Get device type
            dev_type = broadlink_dev.type
            if "RM4PRO" in str(dev_type).upper() or "RM4 PRO" in str(dev_type).upper():
                device_type = DeviceType.BROADLINK_IR
                capabilities = [
                    DeviceCapability.IR_SEND,
                    DeviceCapability.IR_LEARN,
                    DeviceCapability.RF_SEND,
                    DeviceCapability.RF_LEARN,
                ]
            elif "RM4MINI" in str(dev_type).upper():
                device_type = DeviceType.BROADLINK_IR
                capabilities = [
                    DeviceCapability.IR_SEND,
                    DeviceCapability.IR_LEARN,
                ]
            else:
                device_type = DeviceType.BROADLINK_IR
                capabilities = [DeviceCapability.IR_SEND]
            
            # Create device ID from MAC
            mac = broadlink_dev.mac.hex().upper()
            device_id = f"broadlink_{mac}"
            
            # Get hostname as name
            name = broadlink_dev.name or f"BroadLink-{mac[-6:]}"
            ip = broadlink_dev.host[0]
            
            return Device(
                id=device_id,
                name=name,
                device_type=device_type,
                ip_address=ip,
                mac_address=":".join([mac[i:i+2] for i in range(0, 12, 2)]),
                manufacturer="BroadLink",
                model=str(dev_type),
                capabilities=capabilities,
            )
            
        except Exception as e:
            logger.error(f"Error creating BroadLink device: {e}")
            return None
    
    async def _discover_network_devices(self):
        """Discover devices via network scan."""
        import subprocess
        import re
        
        try:
            # Get ARP table
            result = subprocess.run(
                ["ip", "neigh", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse ARP entries
            for line in result.stdout.strip().split("\n"):
                if not line or "FAILED" in line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[0]
                    mac = parts[2]
                    
                    # Skip already discovered devices
                    if any(d.ip_address == ip for d in self.devices.values()):
                        continue
                    
                    # Identify device by OUI
                    manufacturer = await self._identify_manufacturer(mac)
                    device_type = self._infer_device_type(manufacturer)
                    
                    device_id = f"network_{mac.replace(':', '').lower()}"
                    
                    # Only add recognized devices
                    if device_type != DeviceType.UNKNOWN:
                        device = Device(
                            id=device_id,
                            name=f"{manufacturer} ({ip})",
                            device_type=device_type,
                            ip_address=ip,
                            mac_address=mac,
                            manufacturer=manufacturer,
                        )
                        self.devices[device_id] = device
                        logger.info(f"✅ Found network device: {manufacturer} @ {ip}")
                        
        except Exception as e:
            logger.error(f"Error discovering network devices: {e}")
    
    async def _identify_manufacturer(self, mac: str) -> str:
        """Identify manufacturer from MAC OUI."""
        import sys
        sys.path.insert(0, "/home/nlaguna/.openclaw/workspace/scripts")
        
        try:
            from mac_lookup import load_oui_database, parse_mac
            
            oui_db = load_oui_database()
            oui = parse_mac(mac)
            
            if oui:
                return oui_db.get(oui, "Unknown")
        except Exception:
            pass
        
        return "Unknown"
    
    def _infer_device_type(self, manufacturer: str) -> DeviceType:
        """Infer device type from manufacturer."""
        manufacturer_lower = manufacturer.lower()
        
        if "broadlink" in manufacturer_lower:
            return DeviceType.BROADLINK_IR
        elif "amazon" in manufacturer_lower:
            return DeviceType.ALEXA_ECHO
        elif "google" in manufacturer_lower:
            return DeviceType.CHROMECAST
        elif "tuya" in manufacturer_lower:
            return DeviceType.TUYA_DEVICE
        elif "midea" in manufacturer_lower:
            return DeviceType.MIDEA_AC
        elif "raspberry" in manufacturer_lower:
            return DeviceType.UNKNOWN
        else:
            return DeviceType.UNKNOWN
    
    async def send_command(
        self,
        device_id: str,
        command: str,
        **kwargs
    ) -> bool:
        """Send command to device."""
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return False
        
        # Route to appropriate handler
        if device.device_type in [DeviceType.BROADLINK_IR, DeviceType.BROADLINK_RF]:
            return await self._send_broadlink_command(device, command, **kwargs)
        else:
            logger.warning(f"Cannot send commands to {device.device_type}")
            return False
    
    async def _send_broadlink_command(
        self,
        device: Device,
        command: str,
        **kwargs
    ) -> bool:
        """Send command to BroadLink device."""
        try:
            import broadlink
            
            # Load saved codes
            import json
            from pathlib import Path
            
            codes_file = Path.home() / ".openclaw" / "workspace" / "scripts" / "broadlink_codes.json"
            if codes_file.exists():
                with open(codes_file) as f:
                    codes = json.load(f)
            else:
                codes = {}
            
            # Get code for command
            # Command format: "device_command" e.g., "tv_power", "ac_cool_24"
            code_data = codes.get(command)
            if not code_data:
                logger.error(f"Command not found: {command}")
                return False
            
            # Connect to device
            dev = broadlink.hello(device.ip_address)
            if not dev:
                logger.error(f"Cannot connect to {device.name}")
                return False
            
            dev.auth()
            
            # Send command
            if "ir" in code_data:
                dev.send_data(bytes.fromhex(code_data["ir"]))
                logger.info(f"✅ Sent IR command: {command}")
            elif "rf" in code_data:
                dev.send_data(bytes.fromhex(code_data["rf"]))
                logger.info(f"✅ Sent RF command: {command}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    async def learn_command(
        self,
        device_id: str,
        command_name: str,
        command_type: str = "ir"
    ) -> Optional[str]:
        """Learn new IR/RF command from device."""
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return None
        
        if command_type not in ["ir", "rf"]:
            logger.error(f"Invalid command type: {command_type}")
            return None
        
        try:
            import broadlink
            
            dev = broadlink.hello(device.ip_address)
            if not dev:
                return None
            
            dev.auth()
            
            logger.info(f"📻 Learning {command_type.upper()} command: {command_name}")
            logger.info("Press the button on your remote...")
            
            # Enter learning mode
            if command_type == "ir":
                dev.enter_learning()
            else:
                dev.enter_learning_rf()
            
            # Wait for signal
            await asyncio.sleep(5)
            
            # Get learned signal
            data = dev.check_data()
            if data:
                hex_data = data.hex()
                logger.info(f"✅ Learned command: {hex_data[:40]}...")
                return hex_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error learning command: {e}")
            return None
    
    async def get_temperature(self, device_id: str) -> Optional[float]:
        """Get temperature from device with sensor."""
        device = self.devices.get(device_id)
        if not device:
            return None
        
        try:
            import broadlink
            
            dev = broadlink.hello(device.ip_address)
            if not dev:
                return None
            
            dev.auth()
            
            # Check for RM4 series with sensor
            temp = dev.check_temperature()
            return temp
            
        except Exception as e:
            logger.error(f"Error getting temperature: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up device manager...")
        self.devices.clear()