"""
Pattern Learner - Machine Learning for home automation patterns
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class DeviceEvent:
    """Represents a device state change event."""
    device_id: str
    action: str
    timestamp: datetime
    weekday: int
    hour: int
    minute: int
    context: dict = field(default_factory=dict)


@dataclass
class Pattern:
    """Represents a learned automation pattern."""
    id: str
    name: str
    device_id: str
    actions: list[str]
    schedule: dict  # {"days": [0,1,2,3,4], "time": "08:00"}
    confidence: float
    occurrences: int
    first_seen: datetime
    last_seen: datetime


class PatternLearner:
    """Learns and predicts home automation patterns."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".smart_home_brain" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.events: list[DeviceEvent] = []
        self.patterns: dict[str, Pattern] = {}
        self.event_counts: dict[tuple, int] = defaultdict(int)
        
        # ML model
        self.scaler = StandardScaler()
        self.model = DBSCAN(eps=0.5, min_samples=3)
        
    async def record_event(
        self,
        device_id: str,
        action: str,
        context: Optional[dict] = None
    ):
        """Record a device event for pattern learning."""
        now = datetime.now()
        
        event = DeviceEvent(
            device_id=device_id,
            action=action,
            timestamp=now,
            weekday=now.weekday(),
            hour=now.hour,
            minute=now.minute,
            context=context or {},
        )
        
        self.events.append(event)
        self._update_counts(event)
        
        logger.info(f"📝 Recorded event: {device_id} -> {action} at {now.hour:02d}:{now.minute:02d}")
        
        # Check if this matches a known pattern
        await self._check_patterns(event)
        
        # Save to disk
        await self._save_event(event)
        
    def _update_counts(self, event: DeviceEvent):
        """Update event occurrence counts."""
        key = (
            event.device_id,
            event.action,
            event.weekday,
            event.hour,
        )
        self.event_counts[key] += 1
        
    async def _check_patterns(self, event: DeviceEvent):
        """Check if event matches known patterns."""
        for pattern in self.patterns.values():
            if pattern.device_id != event.device_id:
                continue
                
            # Check schedule match
            if event.weekday in pattern.schedule.get("days", []):
                schedule_time = pattern.schedule.get("time", "00:00")
                schedule_hour, schedule_min = map(int, schedule_time.split(":"))
                
                # Allow 15 minute window
                if abs(event.hour * 60 + event.minute - schedule_hour * 60 - schedule_min) <= 15:
                    logger.info(f"🔄 Pattern matched: {pattern.name}")
                    pattern.last_seen = event.timestamp
                    pattern.occurrences += 1
                    
    async def _save_event(self, event: DeviceEvent):
        """Save event to disk."""
        events_file = self.data_dir / "events.jsonl"
        
        with open(events_file, "a") as f:
            f.write(json.dumps({
                "device_id": event.device_id,
                "action": event.action,
                "timestamp": event.timestamp.isoformat(),
                "weekday": event.weekday,
                "hour": event.hour,
                "minute": event.minute,
                "context": event.context,
            }) + "\n")
            
    async def load_patterns(self):
        """Load learned patterns from disk."""
        patterns_file = self.data_dir / "patterns.json"
        
        if not patterns_file.exists():
            logger.info("No existing patterns found")
            return
            
        try:
            with open(patterns_file) as f:
                data = json.load(f)
                
            for pattern_data in data.get("patterns", []):
                pattern = Pattern(
                    id=pattern_data["id"],
                    name=pattern_data["name"],
                    device_id=pattern_data["device_id"],
                    actions=pattern_data["actions"],
                    schedule=pattern_data["schedule"],
                    confidence=pattern_data["confidence"],
                    occurrences=pattern_data["occurrences"],
                    first_seen=datetime.fromisoformat(pattern_data["first_seen"]),
                    last_seen=datetime.fromisoformat(pattern_data["last_seen"]),
                )
                self.patterns[pattern.id] = pattern
                
            logger.info(f"✅ Loaded {len(self.patterns)} patterns")
            
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            
    async def save_patterns(self):
        """Save learned patterns to disk."""
        patterns_file = self.data_dir / "patterns.json"
        
        data = {
            "patterns": [
                {
                    "id": p.id,
                    "name": p.name,
                    "device_id": p.device_id,
                    "actions": p.actions,
                    "schedule": p.schedule,
                    "confidence": p.confidence,
                    "occurrences": p.occurrences,
                    "first_seen": p.first_seen.isoformat(),
                    "last_seen": p.last_seen.isoformat(),
                }
                for p in self.patterns.values()
            ]
        }
        
        with open(patterns_file, "w") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"💾 Saved {len(self.patterns)} patterns")
        
    async def learn_patterns(self) -> list[Pattern]:
        """Learn patterns from recorded events."""
        if len(self.events) < 10:
            logger.warning("Not enough events to learn patterns")
            return []
            
        logger.info("🧠 Learning patterns from events...")
        
        # Prepare data for clustering
        X = []
        event_mapping = []
        
        for event in self.events:
            # Features: weekday (normalized), hour (normalized), minute (normalized)
            X.append([
                event.weekday / 6.0,
                event.hour / 23.0,
                event.minute / 59.0,
            ])
            event_mapping.append(event)
            
        X = np.array(X)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Cluster events
        labels = self.model.fit_predict(X_scaled)
        
        # Extract patterns from clusters
        new_patterns = []
        
        for label in set(labels):
            if label == -1:  # Noise
                continue
                
            cluster_events = [
                event_mapping[i]
                for i, l in enumerate(labels)
                if l == label
            ]
            
            if len(cluster_events) < 3:
                continue
                
            # Calculate pattern properties
            device_id = cluster_events[0].device_id
            action = cluster_events[0].action
            days = sorted(set(e.weekday for e in cluster_events))
            hours = [e.hour for e in cluster_events]
            minutes = [e.minute for e in cluster_events]
            
            # Average time
            avg_hour = int(np.mean(hours))
            avg_minute = int(np.mean(minutes))
            
            # Create pattern
            pattern_id = f"{device_id}_{action}_{avg_hour:02d}{avg_minute:02d}"
            
            pattern = Pattern(
                id=pattern_id,
                name=f"{action} at {avg_hour:02d}:{avg_minute:02d} on days {days}",
                device_id=device_id,
                actions=[action],
                schedule={
                    "days": days,
                    "time": f"{avg_hour:02d}:{avg_minute:02d}",
                },
                confidence=len(cluster_events) / len(self.events),
                occurrences=len(cluster_events),
                first_seen=min(e.timestamp for e in cluster_events),
                last_seen=max(e.timestamp for e in cluster_events),
            )
            
            self.patterns[pattern_id] = pattern
            new_patterns.append(pattern)
            
        if new_patterns:
            await self.save_patterns()
            logger.info(f"✅ Learned {len(new_patterns)} new patterns")
            
        return new_patterns
        
    def suggest_automations(self) -> list[dict]:
        """Suggest automations based on learned patterns."""
        suggestions = []
        
        for pattern in self.patterns.values():
            if pattern.confidence > 0.3 and pattern.occurrences >= 5:
                suggestions.append({
                    "type": "schedule",
                    "name": pattern.name,
                    "device_id": pattern.device_id,
                    "action": pattern.actions[0],
                    "schedule": pattern.schedule,
                    "confidence": pattern.confidence,
                })
                
        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)