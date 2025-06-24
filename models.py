"""
Database models for PropTech Intel application.
"""

from app import db
from datetime import datetime

class Property(db.Model):
    """Property model for storing property information."""
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    square_feet = db.Column(db.Integer)
    lot_size = db.Column(db.Float)
    year_built = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Property {self.address}>'

    def to_dict(self):
        """Convert property to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'price': self.price,
            'property_type': self.property_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'square_feet': self.square_feet,
            'lot_size': self.lot_size,
            'year_built': self.year_built,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MarketData(db.Model):
    """Market data model for storing market trends and analytics."""
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    median_price = db.Column(db.Float, nullable=False)
    price_per_sqft = db.Column(db.Float)
    inventory_count = db.Column(db.Integer)
    days_on_market = db.Column(db.Float)
    price_change_percent = db.Column(db.Float)
    date_recorded = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MarketData {self.region} - {self.date_recorded}>'

    def to_dict(self):
        """Convert market data to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'region': self.region,
            'avg_price': self.avg_price,
            'median_price': self.median_price,
            'price_per_sqft': self.price_per_sqft,
            'inventory_count': self.inventory_count,
            'days_on_market': self.days_on_market,
            'price_change_percent': self.price_change_percent,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }