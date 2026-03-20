"""
Example: Basic usage of Smart Home AI Brain
"""

import asyncio
from smart_home_brain.core.device_manager import DeviceManager
from smart_home_brain.ai.llm_client import LLMClient


async def main():
    # Initialize device manager
    device_manager = DeviceManager()
    
    # Discover devices
    print("🔍 Discovering devices...")
    devices = await device_manager.discover_devices()
    
    print(f"\n✅ Found {len(devices)} devices:")
    for device in devices:
        print(f"  - {device.name} ({device.manufacturer}) @ {device.ip_address}")
    
    # Initialize LLM client
    llm_client = LLMClient(model="llama3.2")
    await llm_client.initialize()
    
    # Chat example
    print("\n💬 Chat with Smart Home AI Brain")
    print("Type 'quit' to exit\n")
    
    while True:
        message = input("You: ")
        if message.lower() in ["quit", "exit", "q"]:
            break
            
        response = await llm_client.chat(message)
        print(f"AI: {response}\n")
    
    # Cleanup
    await device_manager.cleanup()
    await llm_client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())