"""Tests for LLM Client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from smart_home_brain.ai.llm_client import LLMClient, Message


@pytest.fixture
def llm_client():
    """Create LLM client instance."""
    return LLMClient(base_url="http://localhost:11434", model="llama3.2")


class TestLLMClient:
    """Tests for LLMClient class."""

    @pytest.mark.asyncio
    async def test_initialize(self, llm_client):
        """Test client initialization."""
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"models": [{"name": "llama3.2"}]}
            mock_get.return_value = mock_response
            
            await llm_client.initialize()
            
            # Should not raise exception
            assert True

    @pytest.mark.asyncio
    async def test_chat(self, llm_client):
        """Test chat functionality."""
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "Test response"}
            }
            mock_post.return_value = mock_response
            
            response = await llm_client.chat("Hello")
            
            assert response == "Test response"

    @pytest.mark.asyncio
    async def test_extract_intent(self, llm_client):
        """Test intent extraction."""
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {
                    "content": '{"intent": "control_device", "device": "tv", "action": "on"}'
                }
            }
            mock_post.return_value = mock_response
            
            intent = await llm_client.extract_intent("Encender la TV")
            
            assert intent["intent"] == "control_device"
            assert intent["device"] == "tv"

    def test_clear_history(self, llm_client):
        """Test clearing chat history."""
        llm_client.history.append(Message(role="user", content="Test"))
        
        llm_client.clear_history()
        
        assert len(llm_client.history) == 0


class TestMessage:
    """Tests for Message class."""

    def test_message_creation(self):
        """Test message creation."""
        msg = Message(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"