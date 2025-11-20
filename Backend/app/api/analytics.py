"""
Analytics API endpoints.
Provides insights and statistics about leads and conversations.
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.models.lead import Lead, LeadCategory, LeadStatus
from app.core.models.conversation import Conversation
from app.core.rate_limit import limiter

router = APIRouter()
logger = logging.getLogger(__name__)


class TimeSeriesDataPoint(BaseModel):
    """Time series data point."""
    date: str
    value: int


@router.get("/dashboard")
@limiter.limit("30/minute")
async def get_dashboard_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get complete dashboard analytics."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total conversations
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.started_at >= start_date
    ).scalar()
    
    # Completed conversations
    completed_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.started_at >= start_date,
        Conversation.is_completed == True
    ).scalar()
    
    # Leads over time
    daily_leads = db.query(
        func.date(Lead.created_at).label('date'),
        func.count(Lead.id).label('count')
    ).filter(
        Lead.created_at >= start_date
    ).group_by(func.date(Lead.created_at)).order_by('date').all()
    
    leads_over_time = [
        {"date": date.isoformat(), "value": count}
        for date, count in daily_leads
    ]
    
    # Score distribution
    score_distribution = {
        "0-20": db.query(func.count(Lead.id)).filter(Lead.score >= 0, Lead.score < 20).scalar(),
        "20-40": db.query(func.count(Lead.id)).filter(Lead.score >= 20, Lead.score < 40).scalar(),
        "40-60": db.query(func.count(Lead.id)).filter(Lead.score >= 40, Lead.score < 60).scalar(),
        "60-80": db.query(func.count(Lead.id)).filter(Lead.score >= 60, Lead.score < 80).scalar(),
        "80-100": db.query(func.count(Lead.id)).filter(Lead.score >= 80, Lead.score <= 100).scalar(),
    }
    
    return {
        "total_conversations": total_conversations,
        "completed_conversations": completed_conversations,
        "leads_over_time": leads_over_time,
        "score_distribution": score_distribution
    }