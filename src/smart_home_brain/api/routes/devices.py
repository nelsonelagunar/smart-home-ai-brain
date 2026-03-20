"""Device management routes."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from smart_home_brain.core.device_manager import device_manager

router = APIRouter()


@router.get("/")
async def list_devices():
    """List all discovered devices."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    return {
        "devices": [d.to_dict() for d in device_manager.devices.values()],
        "total": len(device_manager.devices),
    }


@router.get("/{device_id}")
async def get_device(device_id: str):
    """Get device by ID."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    device = device_manager.devices.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    return device.to_dict()


@router.post("/{device_id}/send")
async def send_command(device_id: str, command: str, data: Optional[dict] = None):
    """Send command to device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    success = await device_manager.send_command(device_id, command, **(data or {}))
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to send command")
        
    return {"status": "success", "device_id": device_id, "command": command}


@router.post("/{device_id}/learn")
async def learn_command(device_id: str, command_name: str, command_type: str = "ir"):
    """Learn new command from device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    hex_code = await device_manager.learn_command(device_id, command_name, command_type)
    
    if not hex_code:
        raise HTTPException(status_code=400, detail="Failed to learn command")
        
    return {
        "status": "success",
        "device_id": device_id,
        "command_name": command_name,
        "hex_code": hex_code[:50] + "...",
    }


@router.get("/{device_id}/temperature")
async def get_temperature(device_id: str):
    """Get temperature from device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    temp = await device_manager.get_temperature(device_id)
    
    if temp is None:
        raise HTTPException(status_code=400, detail="Cannot get temperature")
        
    return {"device_id": device_id, "temperature": temp}