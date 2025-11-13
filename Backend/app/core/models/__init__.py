"""
Core models package.
Contains all database models for the application.
"""

from app.core.models.lead import (
    Lead,
    LeadStatus,
    LeadCategory,
    ProjectType,
)
from app.core.models.conversation import Conversation
from app.core.models.message import Message, MessageRole, MessageTemplate

__all__ = [
    # Models
    "Lead",
    "Conversation",
    "Message",
    # Enums
    "LeadStatus",
    "LeadCategory",
    "ProjectType",
    "MessageRole",
    "MessageTemplate",
]