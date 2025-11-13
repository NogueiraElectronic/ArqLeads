"""
Chat API endpoints.
Handles chat conversations and message processing.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.models.lead import Lead
from app.core.models.conversation import Conversation
from app.core.models.message import Message, MessageRole, MessageTemplate
from app.core.services.chat_service import ChatService


router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = ChatService()


# Pydantic models for API
class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    session_id: Optional[str] = Field(None, description="Session ID (auto-generated if not provided)")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class ChatMessageResponse(BaseModel):
    """Response model for chat message."""
    session_id: str
    message: str
    role: str
    timestamp: datetime
    lead_score: Optional[int] = None
    lead_category: Optional[str] = None


class ConversationHistory(BaseModel):
    """Model for conversation history."""
    session_id: str
    messages: List[dict]
    lead_info: Optional[dict]
    created_at: datetime
    is_active: bool


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot and get a response.
    """
    try:
        # Generate or validate session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                session_id=session_id,
                channel=request.metadata.get("channel", "web"),
                ip_address=request.metadata.get("ip_address"),
                user_agent=request.metadata.get("user_agent"),
            )
            db.add(conversation)
            
            # Create new lead
            lead = Lead(
                session_id=session_id,
                source=request.metadata.get("source", "web_chat"),
                utm_source=request.metadata.get("utm_source"),
                utm_medium=request.metadata.get("utm_medium"),
                utm_campaign=request.metadata.get("utm_campaign"),
            )
            db.add(lead)
            conversation.lead = lead
            
            db.commit()
            db.refresh(conversation)
            db.refresh(lead)
            
            # Send welcome message
            welcome_msg = MessageTemplate.format(
                MessageTemplate.WELCOME,
                bot_name=settings.CHATBOT_NAME,
                studio_name=settings.STUDIO_NAME
            )
            
            welcome_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=welcome_msg,
            )
            db.add(welcome_message)
            conversation.add_message_count(is_user=False)
            
            db.commit()
            
            return ChatMessageResponse(
                session_id=session_id,
                message=welcome_msg,
                role="assistant",
                timestamp=datetime.utcnow(),
            )
        
        # Check if conversation has timed out
        if conversation.is_timeout(settings.CHATBOT_TIMEOUT_MINUTES):
            conversation.end_conversation()
            db.commit()
            
            return ChatMessageResponse(
                session_id=session_id,
                message="Lo siento, la conversacion ha expirado por inactividad. Quieres comenzar de nuevo?",
                role="assistant",
                timestamp=datetime.utcnow(),
            )
        
        # Get lead
        lead = conversation.lead
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lead not found for conversation"
            )
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
        )
        db.add(user_message)
        conversation.add_message_count(is_user=True)
        
        # Extract information from user message
        chat_service.extract_information(request.message, lead)
        
        # Get conversation history
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        conversation_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        # Generate AI response (always use AI, no rigid templates)
        try:
            # Prepare comprehensive context for AI
            context = {
                "project_type": lead.project_type.value if lead.project_type else None,
                "budget": lead.budget,
                "timeline": lead.timeline,
                "location": lead.location,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "lead_score": lead.score,
                "lead_category": lead.category.value if lead.category else None,
                "has_budget": lead.has_budget,
                "has_timeline": lead.has_timeline,
                "has_location": lead.has_location,
                "contact_complete": lead.contact_complete,
            }

            assistant_response, tokens_used, processing_time = await chat_service.generate_response(
                conversation_history,
                context=context
            )
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            assistant_response = MessageTemplate.format(
                MessageTemplate.ERROR,
                contact_email=settings.NOTIFICATION_EMAILS[0] if settings.NOTIFICATION_EMAILS else "contacto@estudio.com",
                contact_phone="N/A"
            )
            tokens_used = 0
            processing_time = 0
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=assistant_response,
            tokens_used=tokens_used,
            processing_time_ms=processing_time,
            model_used=settings.get_ai_config()["model"],
            provider=settings.AI_PROVIDER,
        )
        db.add(assistant_message)
        conversation.add_message_count(is_user=False)
        
        # Update lead
        lead.conversation_count = conversation.message_count
        
        # Check if lead is hot
        if lead.is_hot_lead() and not lead.contacted_at:
            logger.info(f"Hot lead detected: {lead.id}")
        
        db.commit()
        
        return ChatMessageResponse(
            session_id=session_id,
            message=assistant_response,
            role="assistant",
            timestamp=datetime.utcnow(),
            lead_score=lead.score,
            lead_category=lead.category.value,
        )
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) if settings.DEBUG else "An error occurred"
        )


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history for a session."""
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()
    
    return ConversationHistory(
        session_id=session_id,
        messages=[msg.to_dict() for msg in messages],
        lead_info=conversation.lead.to_dict() if conversation.lead else None,
        created_at=conversation.started_at,
        is_active=conversation.is_active,
    )


@router.post("/end/{session_id}")
async def end_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """End a conversation session."""
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.end_conversation()
    db.commit()
    
    return {"message": "Conversation ended successfully"}
