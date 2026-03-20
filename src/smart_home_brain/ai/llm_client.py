"""
LLM Client - Interface to local LLM via Ollama
"""

import json
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Chat message."""
    role: str  # system, user, assistant
    content: str


class LLMClient:
    """Client for local LLM via Ollama."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.history: list[Message] = []
        
        # System prompt for smart home context
        self.system_prompt = """You are a smart home assistant. You help users control their home devices.

Your capabilities:
- Control BroadLink IR/RF devices (TV, A/C, lights, etc.)
- Get temperature and humidity readings
- Suggest automations based on patterns
- Answer questions about the home state

When the user asks you to control a device:
1. Identify the device and action
2. Use the available tools to execute the action
3. Confirm the action was completed

Always be helpful and concise. Respond in the same language as the user.

Available devices will be provided in the context.
"""
        
    async def initialize(self):
        """Initialize LLM client."""
        # Check if Ollama is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m["name"] for m in models]
                    logger.info(f"✅ Ollama connected. Available models: {model_names}")
                    
                    # Check if model is available
                    if not any(self.model in name for name in model_names):
                        logger.warning(f"⚠️ Model {self.model} not found. Available: {model_names}")
                        
            except Exception as e:
                logger.error(f"❌ Cannot connect to Ollama: {e}")
                
    async def chat(
        self,
        message: str,
        context: Optional[dict] = None,
    ) -> str:
        """Send message to LLM and get response."""
        
        # Build messages
        messages = [
            Message(role="system", content=self.system_prompt),
        ]
        
        # Add context if provided
        if context:
            context_msg = f"Current context:\n{json.dumps(context, indent=2)}"
            messages.append(Message(role="system", content=context_msg))
            
        # Add history (last 10 messages)
        messages.extend(self.history[-10:])
        
        # Add user message
        messages.append(Message(role="user", content=message))
        
        # Call Ollama API
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": m.role, "content": m.content}
                            for m in messages
                        ],
                        "stream": False,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assistant_message = data.get("message", {}).get("content", "")
                    
                    # Update history
                    self.history.append(Message(role="user", content=message))
                    self.history.append(Message(role="assistant", content=assistant_message))
                    
                    return assistant_message
                else:
                    logger.error(f"LLM error: {response.status_code} - {response.text}")
                    return "Lo siento, hubo un error al procesar tu mensaje."
                    
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return "Lo siento, no pude conectar con el modelo de IA."
            
    async def extract_intent(self, message: str) -> Optional[dict]:
        """Extract intent and entities from message."""
        
        prompt = f"""Analyze this message and extract the intent and entities.

Message: "{message}"

Respond in JSON format:
{{
    "intent": "control_device" | "get_temperature" | "get_status" | "set_schedule" | "unknown",
    "device": "device name or id",
    "action": "on" | "off" | "increase" | "decrease" | "set",
    "value": "temperature value or other setting",
    "confidence": 0.0-1.0
}}

Only respond with the JSON, no other text."""

        response = await self.chat(prompt)
        
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
                
        except json.JSONDecodeError:
            logger.warning(f"Could not parse intent: {response}")
            
        return None
        
    async def suggest_action(self, context: dict) -> Optional[str]:
        """Suggest action based on context."""
        
        prompt = f"""Based on the current context, suggest an action if appropriate.

Context: {json.dumps(context, indent=2)}

Consider:
- Time of day
- Temperature
- Device states
- Recent patterns

If you have a suggestion, respond with a short sentence. If no action is needed, respond with "No action suggested"."""

        response = await self.chat(prompt)
        
        if "no action" in response.lower():
            return None
            
        return response
        
    def clear_history(self):
        """Clear chat history."""
        self.history.clear()
        
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up LLM client...")
        self.history.clear()