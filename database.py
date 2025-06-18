"""
Database configuration and utilities for the Competitive Agent application.
"""

import sqlite3
from config import Config

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