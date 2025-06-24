"""
PropTech Intel Flask Application
Main application file containing the Flask app instance and routes.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-fallback-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # Fallback to SQLite for development if no PostgreSQL available
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///proptech_intel.db"
    
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Import models (create this file if you have database models)
try:
    import models
except ImportError:
    logging.info("No models.py file found - database models not loaded")

# Routes
@app.route('/')
def index():
    """Main landing page for PropTech Intel."""
    return render_template('index.html', title="PropTech Intel")

@app.route('/dashboard')
def dashboard():
    """Dashboard page for property analytics."""
    return render_template('dashboard.html', title="Dashboard - PropTech Intel")

@app.route('/api/property-data')
def property_data():
    """API endpoint for property data."""
    # This would typically connect to your data sources
    sample_data = {
        "properties": [
            {"id": 1, "address": "123 Main St", "price": 450000, "type": "Single Family"},
            {"id": 2, "address": "456 Oak Ave", "price": 325000, "type": "Condo"},
        ],
        "market_trends": {
            "avg_price": 387500,
            "price_change": "+5.2%"
        }
    }
    return jsonify(sample_data)

@app.route('/analysis')
def analysis():
    """Property analysis page."""
    return render_template('analysis.html', title="Analysis - PropTech Intel")

@app.route('/reports')
def reports():
    """Reports and insights page."""
    return render_template('reports.html', title="Reports - PropTech Intel")

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html', title="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html', title="Internal Server Error"), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Run the app directly (for development)
    app.run(host='0.0.0.0', port=5000, debug=True)