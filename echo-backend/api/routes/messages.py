"""
Message processing API routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from services.agent_manager import AgentManager
from services.message_queue import MessageQueue
from services.llm_service import llm_service

router = APIRouter()

class Message(BaseModel):
    """Message model"""
    content: str
    platform: str = "generic"
    sender: str
    recipient: Optional[str] = "me"
    subject: Optional[str] = None
    thread_id: Optional[str] = None
    urgency: float = 0.5
    metadata: Dict[str, Any] = {}

class MessageResponse(BaseModel):
    """Message response model"""
    id: str
    original_message: str
    suggested_response: Optional[str]
    action_taken: str
    confidence: float
    timestamp: datetime

class BulkMessages(BaseModel):
    """Bulk message processing"""
    messages: List[Message]
    process_async: bool = False

@router.post("/process")
async def process_message(message: Message, background_tasks: BackgroundTasks):
    """Process a single message"""
    agent_manager = AgentManager()
    
    result = await agent_manager.process_message(
        message=message.content,
        platform=message.platform,
        context={
            "sender": message.sender,
            "recipient": message.recipient,
            "subject": message.subject,
            "thread_id": message.thread_id,
            "urgency": message.urgency,
            **message.metadata
        }
    )
    
    return MessageResponse(
        id=result.get("id", f"msg_{datetime.now().timestamp()}"),
        original_message=message.content,
        suggested_response=result.get("response"),
        action_taken=result.get("action", "processed"),
        confidence=result.get("confidence", 0.0),
        timestamp=datetime.now()
    )

@router.post("/bulk")
async def process_bulk_messages(bulk: BulkMessages, background_tasks: BackgroundTasks):
    """Process multiple messages"""
    agent_manager = AgentManager()
    message_queue = MessageQueue()
    
    if bulk.process_async:
        # Queue messages for background processing
        for message in bulk.messages:
            await message_queue.enqueue(message.dict())
        
        background_tasks.add_task(process_queued_messages, message_queue, agent_manager)
        
        return {
            "status": "queued",
            "message_count": len(bulk.messages),
            "queue_id": f"queue_{datetime.now().timestamp()}"
        }
    else:
        # Process synchronously
        results = []
        for message in bulk.messages:
            result = await agent_manager.process_message(
                message=message.content,
                platform=message.platform,
                context={
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "urgency": message.urgency
                }
            )
            results.append(result)
        
        return {
            "status": "processed",
            "message_count": len(results),
            "results": results
        }

@router.get("/history")
async def get_message_history(
    platform: Optional[str] = None,
    sender: Optional[str] = None,
    limit: int = 50
):
    """Get message processing history"""
    # This would query from database
    return {
        "messages": [],
        "total": 0,
        "filters": {
            "platform": platform,
            "sender": sender,
            "limit": limit
        }
    }

@router.get("/drafts")
async def get_pending_drafts():
    """Get messages waiting for approval"""
    # This would query drafts from database
    return {
        "drafts": [
            {
                "id": "draft_123",
                "original_message": "Can we schedule a meeting?",
                "suggested_response": "I'd be happy to schedule a meeting. What times work for you?",
                "platform": "email",
                "sender": "colleague@example.com",
                "created_at": datetime.now()
            }
        ],
        "total": 1
    }

@router.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: str, edited_response: Optional[str] = None):
    """Approve a draft response"""
    agent_manager = AgentManager()
    
    # Submit feedback to learning system
    if "responder" in agent_manager.agents:
        agent_manager.agents["responder"].learn_from_feedback(
            draft_id=draft_id,
            action="approved" if not edited_response else "edited",
            edited_response=edited_response
        )
    
    return {
        "status": "approved",
        "draft_id": draft_id,
        "response_sent": True
    }

@router.post("/drafts/{draft_id}/reject")
async def reject_draft(draft_id: str, reason: Optional[str] = None):
    """Reject a draft response"""
    agent_manager = AgentManager()
    
    # Submit feedback to learning system
    if "responder" in agent_manager.agents:
        agent_manager.agents["responder"].learn_from_feedback(
            draft_id=draft_id,
            action="rejected"
        )
    
    return {
        "status": "rejected",
        "draft_id": draft_id,
        "reason": reason
    }

@router.get("/templates")
async def get_response_templates(category: Optional[str] = None):
    """Get response templates"""
    templates = {
        "greeting": [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?"
        ],
        "acknowledgment": [
            "Thank you for your message. I'll look into this.",
            "Got it, thanks for letting me know."
        ],
        "scheduling": [
            "I'd be happy to schedule that. What times work best for you?",
            "Let me check my calendar and get back to you with some options."
        ]
    }
    
    if category:
        return templates.get(category, [])
    
    return templates

@router.post("/test-llm")
async def test_llm_generation(message: Message):
    """Test LLM response generation"""
    try:
        # First analyze the message
        analysis = await llm_service.analyze_message_intent(message.content)
        
        # Generate a response
        response = await llm_service.generate_response(
            message=message.content,
            agent_persona=f"You are responding on behalf of {message.recipient}. Be helpful and professional.",
            temperature=0.7
        )
        
        # Enhance based on preferences (example preferences)
        user_preferences = {
            "communication_style": "professional",
            "preferred_tone": "friendly",
            "formality": "medium"
        }
        
        enhanced_response = await llm_service.enhance_response_with_context(
            base_response=response,
            user_preferences=user_preferences,
            message_history=[]
        )
        
        return {
            "original_message": message.content,
            "analysis": analysis,
            "basic_response": response,
            "enhanced_response": enhanced_response,
            "llm_available": llm_service.openai_client is not None or llm_service.anthropic_client is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

async def process_queued_messages(queue: MessageQueue, agent_manager: AgentManager):
    """Background task to process queued messages"""
    while not queue.is_empty():
        message_data = await queue.dequeue()
        if message_data:
            await agent_manager.process_message(
                message=message_data["content"],
                platform=message_data["platform"],
                context=message_data
            )