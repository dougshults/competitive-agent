"""
Data models and utility functions for the Competitive Agent application.
"""

from app import db
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import hashlib
from typing import Optional

class Competitor(db.Model):
    """Competitor model for managing competitor data."""
    __tablename__ = 'competitors'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    website = db.Column(String(255), nullable=False)
    last_scraped = db.Column(DateTime)
    
    # Relationship
    analyses = relationship("Analysis", back_populates="competitor", cascade="all, delete-orphan")
    
    @staticmethod
    def create(name, website):
        """Create a new competitor."""
        competitor = Competitor(name=name, website=website)
        db.session.add(competitor)
        db.session.commit()
        return competitor.id
    
    @staticmethod
    def get_all():
        """Get all competitors."""
        competitors = Competitor.query.all()
        return [{'id': c.id, 'name': c.name, 'website': c.website, 'last_scraped': c.last_scraped} for c in competitors]
    
    @staticmethod
    def get_by_id(competitor_id):
        """Get a competitor by ID."""
        competitor = Competitor.query.get(competitor_id)
        if competitor:
            return {
                'id': competitor.id, 
                'name': competitor.name, 
                'website': competitor.website, 
                'last_scraped': competitor.last_scraped
            }
        return None

class Analysis(db.Model):
    """Analysis model for managing analysis data."""
    __tablename__ = 'analyses'
    
    id = db.Column(Integer, primary_key=True)
    competitor_id = db.Column(Integer, ForeignKey('competitors.id'), nullable=False)
    content = db.Column(Text)
    analysis = db.Column(Text)
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    competitor = relationship("Competitor", back_populates="analyses")
    
    @staticmethod
    def create(competitor_id, content, analysis):
        """Create a new analysis."""
        analysis_obj = Analysis(
            competitor_id=competitor_id,
            content=content,
            analysis=analysis
        )
        db.session.add(analysis_obj)
        db.session.commit()
        return analysis_obj.id
    
    @staticmethod
    def get_latest_by_competitor(competitor_id):
        """Get the latest analysis for a competitor."""
        analysis = Analysis.query.filter_by(competitor_id=competitor_id).order_by(Analysis.timestamp.desc()).first()
        if analysis:
            return {
                'id': analysis.id,
                'competitor_id': analysis.competitor_id,
                'content': analysis.content,
                'analysis': analysis.analysis,
                'timestamp': analysis.timestamp
            }
        return None
    
    @staticmethod
    def get_all_by_competitor(competitor_id):
        """Get all analyses for a competitor."""
        analyses = Analysis.query.filter_by(competitor_id=competitor_id).order_by(Analysis.timestamp.desc()).all()
        return [{
            'id': a.id,
            'competitor_id': a.competitor_id,
            'content': a.content,
            'analysis': a.analysis,
            'timestamp': a.timestamp
        } for a in analyses]

class AISummaryCache(db.Model):
    """AI summary cache for managing cached analysis results.""" 
    __tablename__ = 'ai_summary_cache'
    
    id = db.Column(Integer, primary_key=True)
    content_hash = db.Column(String(64), nullable=False)
    source = db.Column(String(255), nullable=False)
    summary = db.Column(Text, nullable=False)
    created = db.Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_content_hash(content: str) -> str:
        """Generate hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def get_cached_summary(content: str, source: str) -> Optional[str]:
        """Get cached summary if available."""
        content_hash = AISummaryCache.get_content_hash(content)
        cache_entry = AISummaryCache.query.filter_by(
            content_hash=content_hash,
            source=source
        ).order_by(AISummaryCache.created.desc()).first()
        
        return cache_entry.summary if cache_entry else None
    
    @staticmethod
    def set_cached_summary(content: str, source: str, summary: str):
        """Cache a summary."""
        content_hash = AISummaryCache.get_content_hash(content)
        cache_entry = AISummaryCache(
            content_hash=content_hash,
            source=source,
            summary=summary
        )
        db.session.add(cache_entry)
        db.session.commit() 