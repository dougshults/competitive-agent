from analyzer import CompetitiveAnalyzer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analyzer():
    # Initialize analyzer
    analyzer = CompetitiveAnalyzer()
    
    # Test connection
    logger.info("Testing API connection...")
    connection_result = analyzer.test_connection()
    logger.info(f"Connection test result: {connection_result}")
    
    if connection_result["status"] == "success":
        # Test content analysis
        test_content = """
        We are excited to announce our new AI-powered analytics platform that will revolutionize 
        how businesses understand their data. Starting next month, we're introducing a new pricing 
        tier that includes advanced machine learning features. Our platform now supports real-time 
        data processing and automated insights generation.
        """
        
        logger.info("Testing content analysis...")
        analysis = analyzer.analyze_content(test_content, "Test Competitor")
        logger.info(f"Analysis result:\n{analysis}")
        
        # Test caching
        logger.info("Testing cache with same content...")
        cached_analysis = analyzer.analyze_content(test_content, "Test Competitor")
        logger.info(f"Cached analysis result:\n{cached_analysis}")
        
        # Test cache clearing
        logger.info("Testing cache clearing...")
        analyzer.clear_cache()
        
        # Test input validation
        logger.info("Testing input validation...")
        try:
            analyzer.analyze_content("", "Test Competitor")
        except ValueError as e:
            logger.info(f"Expected validation error: {str(e)}")
        
        try:
            analyzer.analyze_content("Some content", "")
        except ValueError as e:
            logger.info(f"Expected validation error: {str(e)}")

if __name__ == "__main__":
    test_analyzer() 