# analyzer.py
import openai
import logging
import time
from typing import Dict, Any, Optional, Union
from functools import lru_cache
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Config = get_config()

class CompetitiveAnalyzer:
    def __init__(self, max_retries: int = 3, retry_delay: int = 1):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.info("CompetitiveAnalyzer initialized")

    def _validate_input(self, content: str, competitor_name: str) -> bool:
        """Validate input parameters."""
        if not content or not isinstance(content, str):
            raise ValueError("Content must be a non-empty string")
        if not competitor_name or not isinstance(competitor_name, str):
            raise ValueError("Competitor name must be a non-empty string")
        return True

    def _preprocess_content(self, content: str) -> str:
        """Preprocess content for analysis."""
        # Remove extra whitespace
        content = ' '.join(content.split())
        # Truncate to 2000 characters
        return content[:2000]

    def _make_api_call(self, messages: list, max_tokens: int) -> Any:
        """Make API call with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=Config.MODEL,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response
            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logger.error(f"API call failed: {str(e)}")
                raise

    def test_connection(self) -> Dict[str, str]:
        """Test the OpenAI API connection."""
        logger.info("Testing API connection")
        try:
            response = self._make_api_call(
                messages=[{"role": "user", "content": "Say 'AI connected!'"}],
                max_tokens=10
            )
            logger.info("API connection successful")
            return {"status": "success", "response": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    @lru_cache(maxsize=100)
    def analyze_content(self, content: str, competitor_name: str) -> str:
        """
        Analyze competitor content with caching.
        
        Args:
            content: The content to analyze
            competitor_name: Name of the competitor
            
        Returns:
            str: Analysis results or error message
        """
        try:
            self._validate_input(content, competitor_name)
            processed_content = self._preprocess_content(content)
            
            if competitor_name == 'PropTech Industry':
                prompt = f"""
                Analyze this PropTech content for competitive intelligence. Format your response with these exact section headers:
                
                Content: {processed_content}
                
                **TECH INNOVATIONS:**
                [Key real estate technology innovations or new products]
                
                **PROPERTY SOLUTIONS:**
                [Notable property management or construction technology solutions]
                
                **SMART BUILDING:**
                [Smart building features or IoT advancements]
                
                **MARKET IMPACT:**
                [Market impact, trends, or shifts]
                
                **COMPETITIVE POSITION:**
                [Potential competitive advantages or threats]
                
                **PARTNERSHIPS & DEALS:**
                [Strategic partnerships, investments, or acquisitions]
                
                **COMPANIES MENTIONED:**
                [List all company names as comma-separated list]
                
                Keep each section concise and actionable.
                """
            else:
                prompt = f"""
                Analyze this content for competitive intelligence. Format your response with these exact section headers:
                
                Content: {processed_content}
                
                **NEW ORGANIZATIONS:**
                [New companies, startups, or organizations mentioned]
                
                **PRODUCT LAUNCHES:**
                [Innovations, product launches, or press releases]
                
                **MARKET POSITIONING:**
                [Market positioning, partnerships, or business models]
                
                **COMPETITIVE THREATS:**
                [Potential competitive advantages or threats]
                
                **RISK AREAS:**
                [Areas of concern, weakness, or risk]
                
                **STRATEGIC IMPLICATIONS:**
                [Strategic implications for the industry]
                
                **INVESTMENT ACTIVITY:**
                [Private equity investment, funding, or acquisitions]
                
                **COMPANIES MENTIONED:**
                [List all company names as comma-separated list]
                
                Keep each section concise and actionable.
                """
            
            logger.info(f"Analyzing content for {competitor_name}")
            response = self._make_api_call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=Config.MAX_TOKENS
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"Analysis completed for {competitor_name}")
            return analysis
            
        except ValueError as ve:
            logger.error(f"Input validation error: {str(ve)}")
            return f"Analysis failed: Invalid input - {str(ve)}"
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return f"Analysis failed: {str(e)}"

    def clear_cache(self):
        """Clear the analysis cache."""
        self.analyze_content.cache_clear()
        logger.info("Analysis cache cleared")