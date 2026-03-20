"""Chat routes for AI interaction."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from smart_home_brain.ai.llm_client import llm_client
from smart_home_brain.core.device_manager import device_manager

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    context: dict = {}


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    intent: dict = {}
    actions: list = []


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI assistant."""
    if not llm_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    # Build context with device info
    context = request.context.copy()
    if device_manager:
        context["devices"] = [d.to_dict() for d in device_manager.devices.values()]
        
    # Get response from LLM
    response = await llm_client.chat(request.message, context)
    
    # Extract intent
    intent = await llm_client.extract_intent(request.message)
    
    # Execute action if intent is control_device
    actions = []
    if intent and intent.get("intent") == "control_device" and device_manager:
        device_name = intent.get("device", "").lower()
        action = intent.get("action", "")
        
        # Find device by name
        device = None
        for d in device_manager.devices.values():
            if device_name in d.name.lower():
                device = d
                break
                
        if device:
            # Map action to command
            command_map = {
                "on": "power_on",
                "off": "power_off",
            }
            command = command_map.get(action, action)
            
            # Try to send command
            success = await device_manager.send_command(device.id, command)
            if success:
                actions.append({
                    "device_id": device.id,
                    "device_name": device.name,
                    "action": action,
                    "status": "success",
                })
                
    return ChatResponse(
        response=response,
        intent=intent or {},
        actions=actions,
    )


@router.post("/suggest")
async def suggest_action():
    """Get AI suggestion based on current context."""
    if not llm_client or not device_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    # Build context
    context = {
        "devices": [d.to_dict() for d in device_manager.devices.values()],
    }
    
    suggestion = await llm_client.suggest_action(context)
    
    return {"suggestion": suggestion}


@router.delete("/history")
async def clear_history():
    """Clear chat history."""
    if not llm_client:
        raise HTTPException(status_code=503, detail="Service not initialized")
        
    llm_client.clear_history()
    
    return {"status": "success", "message": "Chat history cleared"}