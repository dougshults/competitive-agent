"""
Database configuration and utilities for the Competitive Agent application.
"""

import sqlite3
from config import Config
import hashlib
from typing import Optional

def get_db_connection():
    """Get a database connection."""
<<<<<<< HEAD
    # Handle both SQLite URL format and PostgreSQL URL (fallback to SQLite)
    database_url = Config.DATABASE_URL
    if database_url.startswith('postgres'):
        # If PostgreSQL URL is provided, use a local SQLite file instead
        db_path = 'competitive_agent.db'
    else:
        # Handle SQLite URL format
        db_path = database_url.replace('sqlite:///', '') if database_url.startswith('sqlite:///') else database_url
    
    conn = sqlite3.connect(db_path)
=======
    conn = sqlite3.connect(Config.DATABASE_URL.replace('sqlite:///', ''))
>>>>>>> 80b4af1a639f50148534b7d9d0c486a88f307bdb
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
<<<<<<< HEAD
    try:
        conn = get_db_connection()
        content_hash = get_content_hash(content)
        row = conn.execute(
            'SELECT summary FROM ai_summary_cache WHERE content_hash = ? AND source = ? ORDER BY created DESC LIMIT 1',
            (content_hash, source)
        ).fetchone()
        conn.close()
        return row['summary'] if row else None
    except Exception:
        return None

def set_cached_summary(content: str, source: str, summary: str):
    try:
        conn = get_db_connection()
        content_hash = get_content_hash(content)
        conn.execute(
            'INSERT INTO ai_summary_cache (content_hash, source, summary) VALUES (?, ?, ?)',
            (content_hash, source, summary)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Ignore cache errors 
=======
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
>>>>>>> 80b4af1a639f50148534b7d9d0c486a88f307bdb
