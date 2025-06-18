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
        # FIXED: Use the new OpenAI client initialization
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

    def _get_fallback_response(self, content: str, competitor_name: str) -> str:
        """Provide a fallback response when API is unavailable."""
        return f"""
        Note: OpenAI API quota exceeded. Please check your billing status at https://platform.openai.com/account/billing

        Basic Analysis for {competitor_name}:
        1. Content length: {len(content)} characters
        2. Key topics identified: {', '.join(set(content.lower().split()[:5]))}
        3. Status: Analysis limited due to API quota constraints
        
        To get full analysis:
        1. Visit https://platform.openai.com/account/billing
        2. Add payment method or upgrade plan
        3. Try the analysis again
        """

    def _handle_api_error(self, error: Exception) -> Dict[str, str]:
        """Handle different types of API errors with appropriate messages."""
        if isinstance(error, openai.RateLimitError):
            return {
                "status": "error",
                "error": "Rate limit exceeded. Please try again in a few minutes."
            }
        elif isinstance(error, openai.APIError) and "insufficient_quota" in str(error):
            return {
                "status": "error",
                "error": "API quota exceeded. Please check your OpenAI account billing and quota status at https://platform.openai.com/account/billing"
            }
        elif isinstance(error, openai.AuthenticationError):
            return {
                "status": "error",
                "error": "Authentication failed. Please check your API key configuration."
            }
        else:
            return {
                "status": "error",
                "error": f"API error: {str(error)}"
            }

    def _make_api_call(self, messages: list, max_tokens: int) -> Any:
        """Make API call with retry logic."""
        for attempt in range(self.max_retries):
            try:
                # FIXED: Use self.client instead of openai directly
                response = self.client.chat.completions.create(
                    model=Config.MODEL,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response
            except openai.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logger.error(f"API call failed: {str(e)}")
                error_response = self._handle_api_error(e)
                raise Exception(error_response["error"])

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
        """Analyze content using OpenAI's API."""
        try:
            # Check if we're analyzing PropTech content
            if competitor_name == 'PropTech Industry':
                prompt = """Analyze this PropTech content for competitive intelligence focusing on:
1. Real estate technology innovations
2. Property management solutions
3. Construction technology advancements
4. Smart building features
5. Market impact and trends
6. Potential competitive advantages or threats

Content to analyze: """
            else:
                prompt = """Analyze this content for competitive intelligence:
1. Key innovations or features
2. Market positioning
3. Potential competitive advantages
4. Areas of concern or weakness
5. Strategic implications

Content to analyze: """

            # Add content to prompt
            prompt += content

            # Get analysis from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a competitive intelligence analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ DEBUG: Analysis failed: {str(e)}")
            return "Analysis failed due to an error."

    def clear_cache(self):
        """Clear the analysis cache."""
        self.analyze_content.cache_clear()
        logger.info("Analysis cache cleared")