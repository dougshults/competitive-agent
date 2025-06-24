"""
Routes for the Competitive Agent application.
"""

import logging
import time
import asyncio
from flask import jsonify, render_template, request
from models import Competitor, Analysis, AISummaryCache
from analyzer import CompetitiveAnalyzer
from scraper import CompetitiveScraper
import requests
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all routes with the Flask app."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server Error: {error}')
        return render_template('500.html'), 500

    @app.route('/')
    def home():
        """Home page route."""
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f'Error loading home page: {str(e)}')
            return "Error loading page", 500

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
            analyses = Analysis.get_all_by_competitor(competitor_id)
            
            return render_template('competitor.html', competitor=competitor, analyses=analyses)
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
        import urllib
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
            output.append(line)
        
        response = app.response_class(
            '\n'.join(sorted(output)) + '\n',
            mimetype='text/plain'
        )
        return response

    @app.route('/api/competitors')
    def get_competitors():
        """Get all competitors."""
        try:
            competitors = Competitor.get_all()
            return jsonify(competitors)
        except Exception as e:
            logger.error(f'Error getting competitors: {str(e)}')
            return jsonify({"error": "Failed to get competitors"}), 500

    @app.route('/api/test-data')
    def create_test_data():
        """Create test data in the database."""
        try:
            # Create test competitors
            comp1_id = Competitor.create("TechCorp", "https://techcorp.com")
            comp2_id = Competitor.create("InnovateCo", "https://innovateco.com")
            
            # Create test analyses
            Analysis.create(comp1_id, "Sample content 1", "Sample analysis 1")
            Analysis.create(comp2_id, "Sample content 2", "Sample analysis 2")
            
            return jsonify({"message": "Test data created successfully"})
        except Exception as e:
            logger.error(f'Error creating test data: {str(e)}')
            return jsonify({"error": "Failed to create test data"}), 500

    @app.route('/api/competitor/<int:competitor_id>/analyses')
    def get_competitor_analyses(competitor_id):
        """Get all analyses for a specific competitor."""
        try:
            analyses = Analysis.get_all_by_competitor(competitor_id)
            return jsonify(analyses)
        except Exception as e:
            logger.error(f'Error getting analyses for competitor {competitor_id}: {str(e)}')
            return jsonify({"error": "Failed to get analyses"}), 500

    @app.route('/api/ai-test')
    def ai_test():
        try:
            analyzer = CompetitiveAnalyzer()
            result = analyzer.test_connection()
            return jsonify(result)
        except Exception as e:
            logger.error(f'AI test error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/test-analysis')
    def test_analysis():
        try:
            analyzer = CompetitiveAnalyzer()
            test_content = "This is a test content for competitive analysis."
            result = analyzer.analyze_content(test_content, "TestCompetitor")
            return jsonify({"result": result})
        except Exception as e:
            logger.error(f'Test analysis error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/analyze-competitor')
    def analyze_competitor_content():
        try:
            content = request.args.get('content', '')
            competitor = request.args.get('competitor', 'Unknown')
            
            if not content:
                return jsonify({"error": "Content parameter is required"}), 400
            
            analyzer = CompetitiveAnalyzer()
            result = analyzer.analyze_content(content, competitor)
            return jsonify({"analysis": result})
        except Exception as e:
            logger.error(f'Competitor analysis error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/test-scrape')
    def test_scrape():
        scraper = CompetitiveScraper()
        # Fetch the raw RSS feed content for debugging
        feed_url = scraper.sources['techcrunch_main'] if hasattr(scraper, 'sources') and 'techcrunch_main' in scraper.sources else "https://techcrunch.com/feed/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        try:
            response = requests.get(feed_url, headers=headers, timeout=10)
            raw_xml = response.text
            articles = scraper.scrape_rss_feed('techcrunch_main', max_articles=3) if hasattr(scraper, 'scrape_rss_feed') else []
            return {"articles": articles, "raw_xml": raw_xml[:2000]}
        except Exception as e:
            return {"error": str(e), "articles": []}

    @app.route('/api/scrape-and-analyze')
    def scrape_and_analyze():
        try:
            scraper = CompetitiveScraper()
            analyzer = CompetitiveAnalyzer()
            
            # Get articles
            articles = scraper.scrape_proptech_articles(max_articles=3)
            
            if not articles:
                return jsonify({"error": "No articles found"}), 404
            
            results = []
            for article in articles[:2]:  # Limit to 2 for testing
                try:
                    content = f"Title: {article.get('title', '')}\nContent: {article.get('content', '')}"
                    analysis = analyzer.analyze_content(content, article.get('source', 'Unknown'))
                    results.append({
                        "article": article,
                        "analysis": analysis
                    })
                except Exception as e:
                    logger.error(f'Error analyzing article: {str(e)}')
                    results.append({
                        "article": article,
                        "analysis": f"Analysis failed: {str(e)}"
                    })
            
            return jsonify({"results": results})
        except Exception as e:
            logger.error(f'Scrape and analyze error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/test-propmodo')
    def test_propmodo():
        try:
            scraper = CompetitiveScraper()
            articles = scraper.scrape_propmodo(max_articles=3) if hasattr(scraper, 'scrape_propmodo') else []
            return jsonify({"articles": articles})
        except Exception as e:
            logger.error(f'Propmodo test error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/test-all-sources')
    def test_all_sources():
        try:
            scraper = CompetitiveScraper()
            articles = scraper.scrape_all_sources(max_articles_per_source=2) if hasattr(scraper, 'scrape_all_sources') else []
            return jsonify({"articles": articles})
        except Exception as e:
            logger.error(f'All sources test error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/full-analysis')
    def full_competitive_analysis():
        """Endpoint for full competitive analysis of all sources."""
        try:
            scraper = CompetitiveScraper()
            analyzer = CompetitiveAnalyzer()
            
            # Get articles from all sources
            articles = scraper.scrape_proptech_articles(max_articles=10)
            
            if not articles:
                return jsonify({"error": "No articles found"}), 404
            
            analyses = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                def analyze_article(article):
                    try:
                        content = f"Title: {article.get('title', '')}\n\nContent: {article.get('content', '')}"
                        analysis = analyzer.analyze_content(content, article.get('source', 'Unknown'))
                        return {
                            "title": article.get('title', ''),
                            "source": article.get('source', ''),
                            "url": article.get('url', ''),
                            "content": content[:500] + "..." if len(content) > 500 else content,
                            "analysis": analysis,
                            "timestamp": time.time()
                        }
                    except Exception as e:
                        logger.error(f'Error analyzing article {article.get("title", "")}: {str(e)}')
                        return {
                            "title": article.get('title', ''),
                            "source": article.get('source', ''),
                            "error": str(e)
                        }
                
                # Submit all analysis tasks
                futures = [executor.submit(analyze_article, article) for article in articles[:5]]  # Limit to 5
                
                # Collect results
                for future in futures:
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per analysis
                        analyses.append(result)
                    except Exception as e:
                        logger.error(f'Future execution error: {str(e)}')
                        analyses.append({"error": str(e)})
            
            return jsonify({
                "total_articles": len(articles),
                "analyses_completed": len(analyses),
                "analyses": analyses
            })
            
        except Exception as e:
            logger.error(f'Full analysis error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/proptech-articles')
    def proptech_articles():
        try:
            scraper = CompetitiveScraper()
            articles = scraper.scrape_proptech_articles(max_articles=10)
            return jsonify({"articles": articles})
        except Exception as e:
            logger.error(f'PropTech articles error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/proptech-intel')
    def proptech_intelligence():
        """Advanced PropTech intelligence with real-time analysis."""
        try:
            scraper = CompetitiveScraper()
            analyzer = CompetitiveAnalyzer()
            
            # Get fresh PropTech articles
            articles = scraper.scrape_proptech_articles(max_articles=15)
            
            if not articles:
                return jsonify({"message": "No PropTech articles found", "articles": []})
            
            # Async analysis for better performance
            async def analyze_article_async(article):
                try:
                    # Check cache first
                    content = f"Title: {article.get('title', '')}\nContent: {article.get('content', '')}"
                    cached_summary = AISummaryCache.get_cached_summary(content, article.get('source', 'Unknown'))
                    
                    if cached_summary:
                        logger.info(f"Using cached summary for: {article.get('title', '')[:50]}")
                        analysis = cached_summary
                    else:
                        # Perform new analysis
                        analysis = analyzer.analyze_content(content, article.get('source', 'Unknown'))
                        # Cache the result
                        AISummaryCache.set_cached_summary(content, article.get('source', 'Unknown'), analysis)
                    
                    return {
                        "title": article.get('title', ''),
                        "source": article.get('source', ''),
                        "url": article.get('url', ''),
                        "published": article.get('published', ''),
                        "summary": analysis,
                        "cached": cached_summary is not None
                    }
                except Exception as e:
                    logger.error(f'Error analyzing article {article.get("title", "")}: {str(e)}')
                    return {
                        "title": article.get('title', ''),
                        "source": article.get('source', ''),
                        "error": str(e)
                    }
            
            async def analyze_all_articles():
                tasks = [analyze_article_async(article) for article in articles[:8]]  # Limit to 8 for performance
                return await asyncio.gather(*tasks)
            
            # Run async analysis
            try:
                if asyncio.get_event_loop().is_running():
                    # If already in an event loop, use thread pool
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, analyze_all_articles())
                        intel_results = future.result(timeout=60)
                else:
                    intel_results = asyncio.run(analyze_all_articles())
            except Exception as e:
                logger.error(f'Async analysis error: {str(e)}')
                # Fallback to synchronous processing
                intel_results = []
                for article in articles[:5]:  # Reduced for sync processing
                    try:
                        content = f"Title: {article.get('title', '')}\nContent: {article.get('content', '')}"
                        analysis = analyzer.analyze_content(content, article.get('source', 'Unknown'))
                        intel_results.append({
                            "title": article.get('title', ''),
                            "source": article.get('source', ''),
                            "url": article.get('url', ''),
                            "summary": analysis
                        })
                    except Exception as inner_e:
                        logger.error(f'Sync analysis error: {str(inner_e)}')
            
            return jsonify({
                "total_articles_found": len(articles),
                "analyses_completed": len(intel_results),
                "intelligence": intel_results,
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f'PropTech intelligence error: {str(e)}')
            return jsonify({"error": str(e)}), 500

    @app.route('/api/debug-proptech-filter')
    def debug_proptech_filter():
        """Debug endpoint to check PropTech filtering."""
        try:
            scraper = CompetitiveScraper()
            
            # Test some sample texts
            test_texts = [
                "Revolutionary proptech startup raises $50M for smart building solutions",
                "New cryptocurrency reaches all-time high",
                "Real estate technology transforms property management",
                "Apple releases new iPhone model",
                "Property investment platform launches in New York"
            ]
            
            results = []
            for text in test_texts:
                is_relevant = scraper.is_proptech_relevant(text)
                results.append({
                    "text": text,
                    "is_proptech_relevant": is_relevant
                })
            
            return jsonify({
                "debug_results": results,
                "proptech_keywords": scraper.PROPTECH_KEYWORDS[:20]  # First 20 keywords for brevity
            })
            
        except Exception as e:
            logger.error(f'Debug PropTech filter error: {str(e)}')
            return jsonify({"error": str(e)}), 500