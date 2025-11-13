"""
Lead model - Represents a potential customer/client.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    """Lead status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadCategory(str, enum.Enum):
    """Lead category based on scoring."""
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"


class ProjectType(str, enum.Enum):
    """Types of architecture projects."""
    SINGLE_FAMILY = "single_family"
    APARTMENT_REFORM = "apartment_reform"
    NEW_CONSTRUCTION = "new_construction"
    REHABILITATION = "rehabilitation"
    COMMERCIAL = "commercial"
    CONSULTATION = "consultation"
    OTHER = "other"


class Lead(Base):
    """
    Lead model representing a potential customer.
    """
    
    __tablename__ = "leads"

    # Define composite indexes for performance
    __table_args__ = (
        # Composite index for filtering by status and sorting by creation date
        Index('idx_leads_status_created', 'status', 'created_at'),
        # Composite index for filtering by category and sorting by score
        Index('idx_leads_category_score', 'category', 'score'),
        # Index for full-text search on project description (PostgreSQL specific)
        # Index('idx_leads_project_desc_fts', 'project_description', postgresql_using='gin',
        #       postgresql_ops={'project_description': 'gin_trgm_ops'}),
    )

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Information
    name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    
    # Project Information
    project_type = Column(Enum(ProjectType), nullable=True)
    project_description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    budget = Column(Float, nullable=True)
    timeline = Column(String(100), nullable=True)
    timeline_months = Column(Integer, nullable=True)
    
    # Lead Classification
    score = Column(Integer, default=0)
    category = Column(Enum(LeadCategory), default=LeadCategory.COLD, index=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    
    # Qualification Details
    has_defined_project = Column(Boolean, default=False)
    has_budget = Column(Boolean, default=False)
    has_location = Column(Boolean, default=False)
    has_timeline = Column(Boolean, default=False)
    contact_complete = Column(Boolean, default=False)
    
    # Additional Information
    source = Column(String(100), default="web_chat")
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    
    # Session Information
    session_id = Column(String(100), unique=True, index=True)
    conversation_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    contacted_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', category={self.category}, score={self.score})>"
    
    def calculate_score(self) -> int:
        """Calculate lead score based on qualification criteria."""
        from app.core.config import settings
        
        score = 0
        
        if self.has_defined_project:
            score += settings.SCORING_PROJECT_DEFINED
        
        if self.has_budget and self.budget and self.budget >= settings.MIN_BUDGET_THRESHOLD:
            score += settings.SCORING_BUDGET_HIGH
        
        if self.has_timeline and self.timeline_months and self.timeline_months <= settings.MAX_HOT_TIMELINE_MONTHS:
            score += settings.SCORING_TIMELINE_SHORT
        
        if self.contact_complete:
            score += settings.SCORING_CONTACT_COMPLETE
        
        if self.has_location:
            score += settings.SCORING_LOCATION_DEFINED
        
        return min(score, 100)
    
    def update_category(self) -> None:
        """Update lead category based on current score."""
        from app.core.config import settings
        
        if self.score < settings.SCORE_THRESHOLD_COLD:
            self.category = LeadCategory.COLD
        elif self.score < settings.SCORE_THRESHOLD_WARM:
            self.category = LeadCategory.WARM
        else:
            self.category = LeadCategory.HOT
    
    def is_hot_lead(self) -> bool:
        """Check if this is a hot lead."""
        return self.category == LeadCategory.HOT
    
    def is_qualified(self) -> bool:
        """Check if lead meets minimum qualification criteria."""
        return (
            self.has_defined_project and
            self.contact_complete and
            (self.has_budget or self.has_timeline)
        )
    
    def to_dict(self) -> dict:
        """Convert lead to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "project_type": self.project_type.value if self.project_type else None,
            "project_description": self.project_description,
            "location": self.location,
            "budget": self.budget,
            "timeline": self.timeline,
            "score": self.score,
            "category": self.category.value,
            "status": self.status.value,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }