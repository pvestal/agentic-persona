"""
Message queue service for async processing
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class MessageQueue:
    """Simple in-memory message queue (use Redis/RabbitMQ in production)"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = {}
        self.processed = []
        self.failed = []
        
    async def enqueue(self, message: Dict[str, Any]) -> str:
        """Add message to queue"""
        message_id = f"msg_{datetime.now().timestamp()}"
        message["id"] = message_id
        message["queued_at"] = datetime.now().isoformat()
        
        await self.queue.put(message)
        return message_id
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get message from queue"""
        try:
            message = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            self.processing[message["id"]] = message
            return message
        except asyncio.TimeoutError:
            return None
    
    def mark_processed(self, message_id: str):
        """Mark message as processed"""
        if message_id in self.processing:
            message = self.processing.pop(message_id)
            message["processed_at"] = datetime.now().isoformat()
            self.processed.append(message)
    
    def mark_failed(self, message_id: str, error: str):
        """Mark message as failed"""
        if message_id in self.processing:
            message = self.processing.pop(message_id)
            message["failed_at"] = datetime.now().isoformat()
            message["error"] = error
            self.failed.append(message)
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def get_processing_count(self) -> int:
        """Get number of messages being processed"""
        return len(self.processing)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queued": self.get_queue_size(),
            "processing": self.get_processing_count(),
            "processed": len(self.processed),
            "failed": len(self.failed),
            "total": self.get_queue_size() + self.get_processing_count() + len(self.processed) + len(self.failed)
        }
    
    async def save_state(self):
        """Save queue state to disk"""
        state = {
            "queue": list(self.queue._queue),  # Access internal queue
            "processing": self.processing,
            "processed": self.processed[-100:],  # Keep last 100
            "failed": self.failed[-50:],  # Keep last 50
            "saved_at": datetime.now().isoformat()
        }
        
        state_file = Path("queue_state.json")
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    async def load_state(self):
        """Load queue state from disk"""
        state_file = Path("queue_state.json")
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Restore queue
            for message in state.get("queue", []):
                await self.queue.put(message)
            
            self.processing = state.get("processing", {})
            self.processed = state.get("processed", [])
            self.failed = state.get("failed", [])


class PriorityMessageQueue(MessageQueue):
    """Priority-based message queue"""
    
    def __init__(self):
        super().__init__()
        self.high_priority = asyncio.Queue()
        self.normal_priority = asyncio.Queue()
        self.low_priority = asyncio.Queue()
    
    async def enqueue(self, message: Dict[str, Any]) -> str:
        """Add message to appropriate priority queue"""
        message_id = f"msg_{datetime.now().timestamp()}"
        message["id"] = message_id
        message["queued_at"] = datetime.now().isoformat()
        
        urgency = message.get("urgency", 0.5)
        
        if urgency > 0.8:
            await self.high_priority.put(message)
        elif urgency > 0.3:
            await self.normal_priority.put(message)
        else:
            await self.low_priority.put(message)
        
        return message_id
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get highest priority message"""
        # Check high priority first
        if not self.high_priority.empty():
            message = await self.high_priority.get()
        elif not self.normal_priority.empty():
            message = await self.normal_priority.get()
        elif not self.low_priority.empty():
            message = await self.low_priority.get()
        else:
            return None
        
        self.processing[message["id"]] = message
        return message
    
    def get_queue_size(self) -> int:
        """Get total queue size"""
        return (
            self.high_priority.qsize() +
            self.normal_priority.qsize() +
            self.low_priority.qsize()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detailed queue statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "high_priority": self.high_priority.qsize(),
            "normal_priority": self.normal_priority.qsize(),
            "low_priority": self.low_priority.qsize()
        })
        return base_stats