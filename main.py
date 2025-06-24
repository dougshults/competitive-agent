import os
import logging
from logging.handlers import RotatingFileHandler
import time
import asyncio
from flask import Flask, jsonify, render_template, request
from config import get_config
from database import init_database, test_db, get_db_connection
from models import Competitor, Analysis
from analyzer import CompetitiveAnalyzer
from scraper import CompetitiveScraper
import requests
from concurrent.futures import ThreadPoolExecutor

"""
Competitive Agent
Main entry point for the competitive agent application.
This module handles the initialization and main execution flow of the agent.
"""

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    config = get_config()
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            RotatingFileHandler(
                f'logs/{config.LOG_FILE}',
                maxBytes=config.LOG_MAX_BYTES,
                backupCount=config.LOG_BACKUP_COUNT
            ),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Initialize database
try:
    init_database()
    db_status = test_db()
    logger.info(f"Database status: {db_status}")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    # Continue without database for now

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f'Page not found: {request.url}')
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {error}')
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

# Routes
@app.route('/')
def home():
    """Home page route."""
    logger.info('Home page accessed')
    return jsonify({
        "message": "Competitive Analysis Agent",
        "status": "running"
    })

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/competitor/<int:competitor_id>')
def competitor(competitor_id):
    """Display individual competitor page with analyses."""
    try:
        # Get competitor details
        competitor = Competitor.get_by_id(competitor_id)
        if not competitor:
            return "Competitor not found", 404
        
        # Get analyses for this competitor
        conn = get_db_connection()
        analyses = conn.execute(
            'SELECT * FROM analyses WHERE competitor_id = ? ORDER BY timestamp DESC',
            (competitor_id,)
        ).fetchall()
        conn.close()
        
        # Convert sqlite3.Row objects to dictionaries
        analyses_list = [dict(row) for row in analyses]
        
        return render_template('competitor.html', competitor=competitor, analyses=analyses_list)
    except Exception as e:
        logger.error(f'Error loading competitor page {competitor_id}: {str(e)}')
        return "Error loading competitor page", 500

@app.route('/api/analyze')
def analyze():
    """Analysis endpoint."""
    logger.info('Analysis endpoint accessed')
    return jsonify({
        "endpoint": "analyze",
        "status": "ready"
    })

@app.route('/routes')
def list_routes():
    """List all available routes."""
    output = []
    for rule in app.url_map.iter_rules():
        if rule.methods:
            methods = ','.join(sorted(set(rule.methods) - {'HEAD', 'OPTIONS'}))
        else:
            methods = ''
        output.append(f"{rule.endpoint}: {rule.rule} [{methods}]")
    
    return jsonify({"routes": output})

# Test Routes
@app.route('/api/competitors')
def get_competitors():
    """Get all competitors."""
    logger.info('Competitors list requested')
    return jsonify({"competitors": Competitor.get_all()})

@app.route('/api/test-data')
def create_test_data():
    """Create test data in the database."""
    logger.info('Creating test data')
    try:
        # Create a test competitor
        competitor_id = Competitor.create("OpenAI", "https://openai.com")
        
        # Create a test analysis
        Analysis.create(
            competitor_id, 
            "OpenAI launched new features", 
            "Analysis: Significant product updates detected"
        )
        
        return jsonify({
            "message": "Test data created",
            "competitor_id": competitor_id
        })
    except Exception as e:
        logger.error(f'Error creating test data: {str(e)}')
        return jsonify({
            "error": "Failed to create test data",
            "message": str(e)
        }), 500

@app.route('/api/competitor/<int:competitor_id>/analyses')
def get_competitor_analyses(competitor_id):
    """Get all analyses for a specific competitor."""
    logger.info(f'Fetching analyses for competitor {competitor_id}')
    try:
        # First check if competitor exists
        competitor = Competitor.get_by_id(competitor_id)
        if not competitor:
            logger.warning(f'Competitor {competitor_id} not found')
            return jsonify({
                'error': 'Not Found',
                'message': f'Competitor with ID {competitor_id} not found'
            }), 404

        # Get analyses
        conn = get_db_connection()
        analyses = conn.execute(
            'SELECT * FROM analyses WHERE competitor_id = ? ORDER BY timestamp DESC',
            (competitor_id,)
        ).fetchall()
        conn.close()

        return jsonify({
            "competitor": competitor,
            "analyses": [dict(row) for row in analyses]
        })
    except Exception as e:
        logger.error(f'Error fetching analyses for competitor {competitor_id}: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@app.route('/api/ai-test')
def ai_test():
    analyzer = CompetitiveAnalyzer()
    return analyzer.test_connection()

@app.route('/api/test-analysis')
def test_analysis():
    analyzer = CompetitiveAnalyzer()
    result = analyzer.analyze_content(
        "OpenAI launched GPT-5 with breakthrough capabilities", 
        "OpenAI"
    )
    return {"analysis": result}

@app.route('/api/analyze', methods=['POST'])
def analyze_competitor_content():
    try:
        data = request.get_json()
        competitor_name = data.get('competitor_name')
        content = data.get('content')
        
        if not competitor_name or not content:
            return {"error": "Missing competitor_name or content"}, 400
        
        # Get or create competitor
        competitors = Competitor.get_all()
        competitor = next((c for c in competitors if c['name'] == competitor_name), None)
        
        if not competitor:
            competitor_id = Competitor.create(competitor_name, "manual-entry")
        else:
            competitor_id = competitor['id']
        
        # Analyze content
        analyzer = CompetitiveAnalyzer()
        analysis_result = analyzer.analyze_content(content, competitor_name)
        
        # Save analysis to database
        Analysis.create(competitor_id, content, analysis_result)
        
        return {
            "status": "success",
            "competitor": competitor_name,
            "analysis": analysis_result
        }
        
    except Exception as e:
        logger.error(f'Error in analyze_competitor_content: {str(e)}')
        return {"error": str(e)}, 500

@app.route('/api/test-scrape')
def test_scrape():
    scraper = CompetitiveScraper()
    # Fetch the raw RSS feed content for debugging
    feed_url = scraper.sources['techcrunch_main']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    response = requests.get(feed_url, headers=headers, timeout=10)
    raw_xml = response.text
    articles = scraper.scrape_rss_feed('techcrunch_main', max_articles=3)
    return {"articles": articles, "raw_xml": raw_xml[:2000]}  # Return first 2000 chars for brevity

@app.route('/api/scrape-and-analyze')
def scrape_and_analyze():
    scraper = CompetitiveScraper()
    analyzer = CompetitiveAnalyzer()
    # Scrape fresh articles
    articles = scraper.scrape_rss_feed('techcrunch_main', max_articles=3)
    analyses = []
    for article in articles:
        # Analyze each article with AI
        analysis = analyzer.analyze_content(article['content'], 'TechCrunch')
        analyses.append({
            'article_title': article['title'],
            'article_link': article.get('link', article.get('url', '')),
            'ai_analysis': analysis
        })
    return {"analyses": analyses}

# Check if 'venturebeat' is in sources, otherwise comment out the route
# @app.route('/api/test-venturebeat')
# def test_venturebeat():
#     scraper = CompetitiveScraper()
#     articles = scraper.scrape_rss_feed('venturebeat', max_articles=3)
#     return {"articles": articles}

@app.route('/api/test-propmodo')
def test_propmodo():
    scraper = CompetitiveScraper()
    articles = scraper.scrape_propmodo(max_articles=3)
    return {"articles": articles}

@app.route('/api/test-all-sources')
def test_all_sources():
    scraper = CompetitiveScraper()
    articles = asyncio.run(scraper._scrape_all_sources_async(max_articles_per_source=3))
    return {"articles": articles}

@app.route('/api/full-competitive-analysis', methods=['GET'])
def full_competitive_analysis():
    """Endpoint for full competitive analysis of all sources."""
    try:
        scraper = CompetitiveScraper()
        analyzer = CompetitiveAnalyzer()
        # Get articles from all sources
        articles = scraper.scrape_all_sources(max_articles_per_source=5)
        # Analyze each article
        analysis_results = []
        for article in articles:
            analysis = analyzer.analyze_content(article['content'])
            if analysis:
                analysis_results.append({
                    'article': article,
                    'analysis': analysis
                })
        return jsonify({
            'status': 'success',
            'data': {
                'total_articles': len(articles),
                'analyzed_articles': len(analysis_results),
                'results': analysis_results
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/proptech-articles')
def proptech_articles():
    scraper = CompetitiveScraper()
    articles = scraper.scrape_proptech_articles(max_articles=10)
    return {"articles": articles}

@app.route('/api/proptech-intelligence')
def proptech_intelligence():
    """Advanced PropTech intelligence with real-time analysis."""
    try:
        scraper = CompetitiveScraper()
        articles = scraper.scrape_proptech_articles(max_articles=10)
        
        if not articles:
            return jsonify({"message": "No PropTech articles found", "intelligence": []})
        
        # Try to initialize analyzer and perform AI analysis
        try:
            analyzer = CompetitiveAnalyzer()
            logger.info("CompetitiveAnalyzer initialized successfully")
            
            intel_results = []
            for article in articles[:5]:  # Limit to 5 for performance
                try:
                    content = f"Title: {article.get('title', '')}\nContent: {article.get('content', '')}"
                    
                    # Check cache first
                    cached_summary = get_cached_summary(content, article.get('source', 'Unknown'))
                    
                    if cached_summary:
                        analysis = cached_summary
                        cached = True
                        logger.info(f"Using cached analysis for: {article.get('title', '')[:50]}")
                    else:
                        # Perform AI analysis
                        analysis = analyzer.analyze_content(content, article.get('source', 'Unknown'))
                        set_cached_summary(content, article.get('source', 'Unknown'), analysis)
                        cached = False
                        logger.info(f"Generated new analysis for: {article.get('title', '')[:50]}")
                    
                    intel_results.append({
                        "title": article.get('title', ''),
                        "source": article.get('source', ''),
                        "url": article.get('url', ''),
                        "published": article.get('published', ''),
                        "summary": analysis,
                        "cached": cached
                    })
                except Exception as e:
                    logger.error(f'Error analyzing article {article.get("title", "")}: {str(e)}')
                    intel_results.append({
                        "title": article.get('title', ''),
                        "source": article.get('source', ''),
                        "url": article.get('url', ''),
                        "published": article.get('published', ''),
                        "summary": f"Analysis failed: {str(e)}",
                        "cached": False
                    })
            
            return jsonify({
                "total_articles_found": len(articles),
                "analyses_completed": len(intel_results),
                "intelligence": intel_results,
                "timestamp": time.time(),
                "note": "AI-powered competitive intelligence analysis"
            })
            
        except Exception as e:
            logger.error(f"Could not initialize analyzer: {str(e)}")
            # Fallback to basic article display
            intel_results = []
            for article in articles[:8]:
                intel_results.append({
                    "title": article.get('title', ''),
                    "source": article.get('source', ''),
                    "url": article.get('url', ''),
                    "published": article.get('published', ''),
                    "summary": f"**Source:** {article.get('source', 'Unknown')}\n\n**Content Preview:** {article.get('content', '')[:200]}...\n\n**Note:** AI analysis unavailable - {str(e)}",
                    "cached": False
                })
            
            return jsonify({
                "total_articles_found": len(articles),
                "analyses_completed": len(intel_results),
                "intelligence": intel_results,
                "timestamp": time.time(),
                "note": f"AI analysis temporarily unavailable: {str(e)}"
            })
        
    except Exception as e:
        logger.error(f'PropTech intelligence error: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug-proptech-filter')
def debug_proptech_filter():
    scraper = CompetitiveScraper()
    
    # Get all articles first
    all_articles = asyncio.run(scraper._scrape_all_sources_async(max_articles_per_source=3))
    
    # Check each article against PropTech keywords
    debug_info = []
    for article in all_articles:
        content = f"{article['title']} {article['content']}"
        is_relevant = scraper.is_proptech_relevant(content)
        
        debug_info.append({
            'title': article['title'],
            'source': article['source'],
            'is_proptech': is_relevant,
            'content_preview': content[:200] + "..."
        })
    
    return {
        "total_articles": len(all_articles),
        "debug_info": debug_info
    }

def main():
    """
    Main function that serves as the entry point for the application.
    """
    config = get_config()
    
    # Always return the app for Gunicorn to use
    logger.info(f'Competitive Agent Server configured for port {config.PORT}')
    return app

# For Gunicorn deployment
app = main()

if __name__ == "__main__":
    # For direct execution
    config = get_config()
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG) 