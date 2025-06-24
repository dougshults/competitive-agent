"""
Data models and utility functions for the Competitive Agent application.
"""

from database import get_db_connection
from datetime import datetime

class Competitor:
    """Competitor model for managing competitor data."""
    
    @staticmethod
    def create(name, website):
        """Create a new competitor."""
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO competitors (name, website) VALUES (?, ?)',
            (name, website)
        )
        competitor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return competitor_id
    
    @staticmethod
    def get_all():
        """Get all competitors."""
        conn = get_db_connection()
        competitors = conn.execute('SELECT * FROM competitors').fetchall()
        conn.close()
        return [dict(row) for row in competitors]
    
    @staticmethod
    def get_by_id(competitor_id):
        """Get a competitor by ID."""
        conn = get_db_connection()
        competitor = conn.execute(
            'SELECT * FROM competitors WHERE id = ?', (competitor_id,)
        ).fetchone()
        conn.close()
        return dict(competitor) if competitor else None

class Analysis:
    """Analysis model for managing analysis data."""
    
    @staticmethod
    def create(competitor_id, content, analysis):
        """Create a new analysis."""
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO analyses (competitor_id, content, analysis) VALUES (?, ?, ?)',
            (competitor_id, content, analysis)
        )
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    @staticmethod
    def get_latest_by_competitor(competitor_id):
        """Get the latest analysis for a competitor."""
        conn = get_db_connection()
        analysis = conn.execute(
            'SELECT * FROM analyses WHERE competitor_id = ? ORDER BY timestamp DESC LIMIT 1',
            (competitor_id,)
        ).fetchone()
        conn.close()
        return dict(analysis) if analysis else None 