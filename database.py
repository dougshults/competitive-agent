"""
Database configuration and utilities for the Competitive Agent application.
"""

import sqlite3
from config import Config
import hashlib
from typing import Optional

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(Config.DATABASE_URL.replace('sqlite:///', ''))
    conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    
    # Create competitors table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT NOT NULL,
            last_scraped TIMESTAMP
        )
    ''')
    
    # Create analyses table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER,
            content TEXT,
            analysis TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors (id)
        )
    ''')
    
    # Create ai_summary_cache table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ai_summary_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT NOT NULL,
            source TEXT NOT NULL,
            summary TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def test_db():
    """Test the database connection."""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "Database connection successful"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}

# Helper functions for AI summary cache
def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def get_cached_summary(content: str, source: str) -> Optional[str]:
    conn = get_db_connection()
    content_hash = get_content_hash(content)
    row = conn.execute(
        'SELECT summary FROM ai_summary_cache WHERE content_hash = ? AND source = ? ORDER BY created DESC LIMIT 1',
        (content_hash, source)
    ).fetchone()
    conn.close()
    return row['summary'] if row else None

def set_cached_summary(content: str, source: str, summary: str):
    conn = get_db_connection()
    content_hash = get_content_hash(content)
    conn.execute(
        'INSERT INTO ai_summary_cache (content_hash, source, summary) VALUES (?, ?, ?)',
        (content_hash, source, summary)
    )
    conn.commit()
    conn.close() 