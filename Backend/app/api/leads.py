"""
Leads API endpoints.
Handles lead management and CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.models.lead import Lead, LeadStatus, LeadCategory, ProjectType
from app.core.rate_limit import limiter
from app.core.validators import InputValidator

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic models
class LeadResponse(BaseModel):
    """Response model for lead data."""
    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    project_type: Optional[str]
    project_description: Optional[str]
    location: Optional[str]
    budget: Optional[float]
    timeline: Optional[str]
    score: int
    category: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Response model for list of leads."""
    total: int
    leads: List[LeadResponse]
    page: int
    page_size: int


class LeadUpdateRequest(BaseModel):
    """Request model for updating a lead."""
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize notes field to prevent XSS."""
        if v is None:
            return v
        return InputValidator.sanitize_text_field(v, max_length=5000)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and sanitize tags."""
        if v is None:
            return v
        sanitized_tags = []
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Tag length cannot exceed 50 characters")
            sanitized_tag = InputValidator.sanitize_text_field(tag, max_length=50)
            sanitized_tags.append(sanitized_tag)
        return sanitized_tags


class LeadStatsResponse(BaseModel):
    """Response model for lead statistics."""
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    avg_score: float
    leads_today: int
    leads_this_week: int
    leads_this_month: int


@router.get("/", response_model=LeadListResponse)
@limiter.limit("60/minute")
async def get_leads(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[LeadCategory] = None,
    status: Optional[LeadStatus] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of leads with filtering and pagination."""
    query = db.query(Lead)
    
    # Apply filters
    if category:
        query = query.filter(Lead.category == category)
    
    if status:
        query = query.filter(Lead.status == status)
    
    if min_score is not None:
        query = query.filter(Lead.score >= min_score)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_term)) |
            (Lead.email.ilike(search_term)) |
            (Lead.phone.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    leads = query.order_by(desc(Lead.created_at)).offset(offset).limit(page_size).all()
    
    return LeadListResponse(
        total=total,
        leads=[LeadResponse.from_orm(lead) for lead in leads],
        page=page,
        page_size=page_size
    )


@router.get("/hot", response_model=LeadListResponse)
@limiter.limit("60/minute")
async def get_hot_leads(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get hot leads (high priority)."""
    query = db.query(Lead).filter(
        Lead.category == LeadCategory.HOT,
        Lead.status == LeadStatus.NEW
    )
    
    total = query.count()
    offset = (page - 1) * page_size
    leads = query.order_by(desc(Lead.created_at)).offset(offset).limit(page_size).all()
    
    return LeadListResponse(
        total=total,
        leads=[LeadResponse.from_orm(lead) for lead in leads],
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=LeadStatsResponse)
@limiter.limit("30/minute")
async def get_lead_stats(request: Request, db: Session = Depends(get_db)):
    """Get overall lead statistics."""
    total_leads = db.query(func.count(Lead.id)).scalar()
    
    # Count by category
    hot_leads = db.query(func.count(Lead.id)).filter(Lead.category == LeadCategory.HOT).scalar()
    warm_leads = db.query(func.count(Lead.id)).filter(Lead.category == LeadCategory.WARM).scalar()
    cold_leads = db.query(func.count(Lead.id)).filter(Lead.category == LeadCategory.COLD).scalar()
    
    # Count by status
    new_leads = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.NEW).scalar()
    contacted_leads = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.CONTACTED).scalar()
    qualified_leads = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.QUALIFIED).scalar()
    converted_leads = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.CONVERTED).scalar()
    
    # Average score
    avg_score = db.query(func.avg(Lead.score)).scalar() or 0
    
    # Time-based counts
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    leads_today = db.query(func.count(Lead.id)).filter(Lead.created_at >= today_start).scalar()
    leads_this_week = db.query(func.count(Lead.id)).filter(Lead.created_at >= week_start).scalar()
    leads_this_month = db.query(func.count(Lead.id)).filter(Lead.created_at >= month_start).scalar()
    
    return LeadStatsResponse(
        total_leads=total_leads,
        hot_leads=hot_leads,
        warm_leads=warm_leads,
        cold_leads=cold_leads,
        new_leads=new_leads,
        contacted_leads=contacted_leads,
        qualified_leads=qualified_leads,
        converted_leads=converted_leads,
        avg_score=round(avg_score, 2),
        leads_today=leads_today,
        leads_this_week=leads_this_week,
        leads_this_month=leads_this_month,
    )


@router.get("/{lead_id}", response_model=LeadResponse)
@limiter.limit("60/minute")
async def get_lead(
    request: Request,
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return LeadResponse.from_orm(lead)


@router.patch("/{lead_id}")
@limiter.limit("20/minute")
async def update_lead(
    request: Request,
    lead_id: int,
    update_data: LeadUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update lead information."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Update fields
    if update_data.status is not None:
        lead.status = update_data.status
        
        if update_data.status == LeadStatus.CONTACTED and not lead.contacted_at:
            lead.contacted_at = datetime.utcnow()
        elif update_data.status == LeadStatus.CONVERTED and not lead.converted_at:
            lead.converted_at = datetime.utcnow()
    
    if update_data.notes is not None:
        lead.notes = update_data.notes
    
    if update_data.tags is not None:
        lead.tags = update_data.tags
    
    db.commit()
    db.refresh(lead)
    
    return LeadResponse.from_orm(lead)


@router.delete("/{lead_id}")
@limiter.limit("10/minute")
async def delete_lead(
    request: Request,
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    db.delete(lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}


@router.get("/export/csv")
@limiter.limit("5/minute")
async def export_leads_csv(
    request: Request,
    category: Optional[LeadCategory] = None,
    status: Optional[LeadStatus] = None,
    db: Session = Depends(get_db)
):
    """Export leads to CSV format."""
    import csv
    from io import StringIO
    
    query = db.query(Lead)
    
    if category:
        query = query.filter(Lead.category == category)
    
    if status:
        query = query.filter(Lead.status == status)
    
    leads = query.all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Name", "Email", "Phone", "Project Type", "Location",
        "Budget", "Timeline", "Score", "Category", "Status",
        "Source", "Created At", "Contacted At"
    ])
    
    # Write data
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.name or "",
            lead.email or "",
            lead.phone or "",
            lead.project_type.value if lead.project_type else "",
            lead.location or "",
            lead.budget or "",
            lead.timeline or "",
            lead.score,
            lead.category.value,
            lead.status.value,
            lead.source,
            lead.created_at.isoformat(),
            lead.contacted_at.isoformat() if lead.contacted_at else ""
        ])
    
    csv_data = output.getvalue()
    output.close()
    
    return {
        "filename": f"leads_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        "data": csv_data,
        "count": len(leads)
    }