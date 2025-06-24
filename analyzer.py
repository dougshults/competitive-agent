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
        self.client = openai.OpenAI(
            api_key=Config.OPENAI_API_KEY
        )
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
                system_message = (
                    "You are a competitive intelligence analyst specializing in real estate technology. "
                    "Your job is to extract actionable insights from news and company updates."
                )
                user_prompt = (
                    f"Analyze this PropTech content for competitive intelligence. Format your response with these exact section headers:\n\n"
                    f"Content: {processed_content}\n\n"
                    "**TECH INNOVATIONS:**\n[Key real estate technology innovations or new products]\n\n"
                    "**PROPERTY SOLUTIONS:**\n[Notable property management or construction technology solutions]\n\n"
                    "**SMART BUILDING:**\n[Smart building features or IoT advancements]\n\n"
                    "**MARKET IMPACT:**\n[Market impact, trends, or shifts]\n\n"
                    "**COMPETITIVE POSITION:**\n[Potential competitive advantages or threats]\n\n"
                    "**PARTNERSHIPS & DEALS:**\n[Strategic partnerships, investments, or acquisitions]\n\n"
                    "**COMPANIES MENTIONED:**\n[List all company names as comma-separated list]\n\n"
                    "Respond only with the section headers and their content, no extra commentary. Keep each section concise and actionable."
                )
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ]
            else:
                system_message = (
                    "You are a competitive intelligence analyst specializing in real estate technology. "
                    "Your job is to extract actionable insights from news and company updates."
                )
                user_prompt = (
                    f"Analyze this content for competitive intelligence. Format your response with these exact section headers:\n\n"
                    f"Content: {processed_content}\n\n"
                    "**NEW ORGANIZATIONS:**\n[New companies, startups, or organizations mentioned]\n\n"
                    "**PRODUCT LAUNCHES:**\n[Innovations, product launches, or press releases]\n\n"
                    "**MARKET POSITIONING:**\n[Market positioning, partnerships, or business models]\n\n"
                    "**COMPETITIVE THREATS:**\n[Potential competitive advantages or threats]\n\n"
                    "**RISK AREAS:**\n[Areas of concern, weakness, or risk]\n\n"
                    "**STRATEGIC IMPLICATIONS:**\n[Strategic implications for the industry]\n\n"
                    "**INVESTMENT ACTIVITY:**\n[Private equity investment, funding, or acquisitions]\n\n"
                    "**COMPANIES MENTIONED:**\n[List all company names as comma-separated list]\n\n"
                    "Respond only with the section headers and their content, no extra commentary. Keep each section concise and actionable."
                )
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ]
            logger.info(f"Analyzing content for {competitor_name}")
            response = self._make_api_call(
                messages=messages,
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