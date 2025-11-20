"""
Conversation model - Represents a chat session.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Conversation(Base):
    """
    Conversation model representing a chat session.
    """

    __tablename__ = "conversations"

    # Define indexes for performance
    __table_args__ = (
        # Index for finding active conversations
        Index('idx_conv_active_last_msg', 'is_active', 'last_message_at'),
        # Index for finding conversations by lead
        Index('idx_conv_lead_started', 'lead_id', 'started_at'),
        # Index for analytics queries
        Index('idx_conv_channel_started', 'channel', 'started_at'),
        # Partial index for active conversations only
        Index('idx_conv_active_only', 'session_id', 'last_message_at',
              postgresql_where="is_active = true"),
    )
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Session Identification
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Lead Reference
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Conversation Metadata
    channel = Column(String(50), default="web")
    language = Column(String(10), default="es")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Statistics
    message_count = Column(Integer, default=0)
    user_message_count = Column(Integer, default=0)
    bot_message_count = Column(Integer, default=0)
    
    # Context and State
    context = Column(JSON, default=dict)
    current_step = Column(String(100), nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_message_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    # IP and User Agent
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', messages={self.message_count})>"
    
    def add_message_count(self, is_user: bool = True) -> None:
        """Increment message counters."""
        self.message_count += 1
        if is_user:
            self.user_message_count += 1
        else:
            self.bot_message_count += 1
        self.last_message_at = datetime.utcnow()
    
    def end_conversation(self) -> None:
        """Mark conversation as ended."""
        self.is_active = False
        self.ended_at = datetime.utcnow()
    
    def mark_completed(self) -> None:
        """Mark conversation as completed."""
        self.is_completed = True
        self.end_conversation()
    
    def get_duration_minutes(self) -> float:
        """Calculate conversation duration in minutes."""
        if self.ended_at:
            delta = self.ended_at - self.started_at
        else:
            delta = datetime.utcnow() - self.started_at
        return delta.total_seconds() / 60
    
    def is_timeout(self, timeout_minutes: int = 15) -> bool:
        """Check if conversation has timed out."""
        if not self.is_active:
            return False
        
        delta = datetime.utcnow() - self.last_message_at
        return delta.total_seconds() / 60 > timeout_minutes
    
    def update_context(self, key: str, value: any) -> None:
        """Update conversation context."""
        if not isinstance(self.context, dict):
            self.context = {}
        self.context[key] = value
    
    def get_context(self, key: str, default=None):
        """Get value from conversation context."""
        if not isinstance(self.context, dict):
            return default
        return self.context.get(key, default)
    
    def to_dict(self) -> dict:
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "lead_id": self.lead_id,
            "channel": self.channel,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "message_count": self.message_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_minutes": round(self.get_duration_minutes(), 2),
        }