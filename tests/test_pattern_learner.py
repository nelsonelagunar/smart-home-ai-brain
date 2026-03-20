"""Tests for Pattern Learner."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch
import tempfile

from smart_home_brain.core.pattern_learner import (
    PatternLearner,
    DeviceEvent,
    Pattern,
)


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def pattern_learner(temp_data_dir):
    """Create pattern learner instance."""
    return PatternLearner(data_dir=temp_data_dir)


@pytest.fixture
def sample_event():
    """Create sample device event."""
    return DeviceEvent(
        device_id="broadlink_sala",
        action="tv_power",
        timestamp=datetime.now(),
        weekday=0,
        hour=8,
        minute=30,
    )


class TestDeviceEvent:
    """Tests for DeviceEvent class."""

    def test_event_creation(self, sample_event):
        """Test event creation."""
        assert sample_event.device_id == "broadlink_sala"
        assert sample_event.action == "tv_power"
        assert sample_event.weekday == 0
        assert sample_event.hour == 8


class TestPatternLearner:
    """Tests for PatternLearner class."""

    @pytest.mark.asyncio
    async def test_record_event(self, pattern_learner, sample_event):
        """Test recording an event."""
        await pattern_learner.record_event(
            device_id=sample_event.device_id,
            action=sample_event.action,
        )
        
        assert len(pattern_learner.events) == 1

    @pytest.mark.asyncio
    async def test_load_patterns_empty(self, pattern_learner):
        """Test loading patterns when file doesn't exist."""
        await pattern_learner.load_patterns()
        
        assert len(pattern_learner.patterns) == 0

    @pytest.mark.asyncio
    async def test_save_and_load_patterns(self, pattern_learner):
        """Test saving and loading patterns."""
        # Create a pattern
        pattern = Pattern(
            id="test_pattern",
            name="Test Pattern",
            device_id="broadlink_sala",
            actions=["tv_power"],
            schedule={"days": [0, 1, 2], "time": "08:00"},
            confidence=0.8,
            occurrences=10,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
        )
        
        pattern_learner.patterns["test_pattern"] = pattern
        
        # Save
        await pattern_learner.save_patterns()
        
        # Clear and reload
        pattern_learner.patterns.clear()
        await pattern_learner.load_patterns()
        
        assert len(pattern_learner.patterns) == 1
        assert "test_pattern" in pattern_learner.patterns

    def test_suggest_automations(self, pattern_learner):
        """Test automation suggestions."""
        # Add pattern with high confidence
        pattern = Pattern(
            id="morning_tv",
            name="Morning TV",
            device_id="broadlink_sala",
            actions=["tv_power"],
            schedule={"days": [0, 1, 2, 3, 4], "time": "08:00"},
            confidence=0.7,
            occurrences=20,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
        )
        pattern_learner.patterns["morning_tv"] = pattern
        
        suggestions = pattern_learner.suggest_automations()
        
        assert len(suggestions) == 1
        assert suggestions[0]["device_id"] == "broadlink_sala"