# PropTech Intel - Replit Configuration

## Overview

PropTech Intel is a Flask-based competitive intelligence platform for property technology analysis. The application features AI-powered article analysis, real-time PropTech news scraping, and structured competitive intelligence reporting. Configured for deployment on Replit using Gunicorn with SQLite database backend.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **Static Assets**: Served through Flask's static file handling
- **Templates**: HTML templates with Jinja2 templating engine

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **WSGI Server**: Gunicorn for production deployment
- **Database ORM**: Flask-SQLAlchemy for database operations
- **Session Management**: Flask sessions with configurable secret key

### Development vs Production
- **Development**: Flask development server with auto-reload
- **Production**: Gunicorn with auto-scaling deployment target

## Key Components

### Application Architecture
- **main.py**: Primary Flask application with all routes and endpoints
- **analyzer.py**: OpenAI-powered competitive intelligence analysis engine  
- **scraper.py**: Multi-source PropTech article scraping with content filtering
- **models.py**: Data models for competitors, analyses, and caching
- **database.py**: SQLite database management and helper functions
- **config.py**: Application configuration with environment variable support

### Frontend Interface
- **templates/dashboard.html**: Main PropTech intelligence dashboard interface
- **static/js/app.js**: Interactive article loading and display functionality

### Deployment Configuration
- **.replit**: Replit deployment configuration
  - Python 3.11 runtime
  - PostgreSQL and OpenSSL packages
  - Gunicorn deployment with auto-scaling
  - Parallel workflow execution

## Data Flow

### Request Processing
1. Incoming HTTP requests handled by Gunicorn
2. Flask application processes requests through defined routes
3. Database queries executed through Flask-SQLAlchemy
4. Responses rendered using Jinja2 templates

### Environment Configuration
1. Environment variables loaded from Replit Secrets
2. Configuration validation in replit_config.py
3. Flask app initialization with production settings
4. Database connection established via PostgreSQL

## External Dependencies

### Core Dependencies
- **Flask 3.1.1+**: Web framework
- **Flask-SQLAlchemy 3.1.1+**: Database ORM
- **Gunicorn 23.0.0+**: WSGI server
- **psycopg2-binary 2.9.10+**: PostgreSQL adapter
- **email-validator 2.2.0+**: Email validation utilities

### Runtime Dependencies
- **Python 3.11**: Runtime environment
- **PostgreSQL**: Database server
- **OpenSSL**: Cryptographic functions

### API Integrations
- **OpenAI API**: AI/ML capabilities (API key required)
- **Other APIs**: Configurable through environment variables

## Deployment Strategy

### Replit Deployment
- **Target**: Autoscale deployment for production
- **Port**: 5000 (configurable)
- **Binding**: 0.0.0.0 for external access
- **Process Management**: Gunicorn with port reuse and auto-reload

### Environment Variables
- **SESSION_SECRET**: Flask session encryption key
- **OPENAI_API_KEY**: API access for AI features
- **FLASK_ENV**: Environment setting (production/development)
- **Additional**: Configurable based on application requirements

### Database Strategy
- **Primary**: SQLite for local development and production
- **Models**: Raw SQL with database.py abstraction layer
- **Caching**: AI analysis results cached to improve performance

## Changelog

```
Changelog:
- June 24, 2025. Initial setup
- June 24, 2025. Fixed SQLite database integration and OpenAI API connectivity
- June 24, 2025. Implemented competitive intelligence analysis with structured output
- June 24, 2025. Moved dashboard to root route (/) as primary user interface
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
Deploy actual existing Flask app from GitHub repository, not create new application.
```