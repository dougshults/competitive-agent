import openai
import logging
from functools import lru_cache
from config import get_config
from database import get_cached_summary, set_cached_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Config = get_config()
openai.api_key = Config.OPENAI_API_KEY

class CompetitiveAnalyzer:
    def __init__(self):
        logger.info("CompetitiveAnalyzer initialized")

    @lru_cache(maxsize=100)
    def analyze_content(self, content: str, competitor_name: str) -> str:
        try:
            cached = get_cached_summary(content, competitor_name)
            if cached:
                logger.info(f"Cache hit for {competitor_name} article.")
                return cached
            
            if competitor_name == 'PropTech Industry':
                prompt = "Analyze this PropTech article. Provide numbered points: 1. Key innovations 2. Market impact 3. Companies mentioned 4. Competitive threats 5. Strategic implications. Content: "
            else:
                prompt = "Analyze this article. Provide numbered points: 1. New companies 2. Innovations 3. Market positioning 4. Competitive threats 5. Strategic implications. Content: "
            
            prompt += content
            
            ChatCompletion = getattr(openai, 'ChatCompletion', None)
            Completion = getattr(openai, 'Completion', None)
            if ChatCompletion is not None:
                response = ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a competitive intelligence analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                result = response.choices[0].message['content']
            elif Completion is not None:
                response = Completion.create(
                    model="gpt-4",
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=500
                )
                result = response.choices[0].text
            else:
                raise RuntimeError("No valid OpenAI completion method found.")
            
            set_cached_summary(content, competitor_name, result)
            logger.info(f"Cached new summary for {competitor_name} article.")
            return result
            
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def clear_cache(self):
        self.analyze_content.cache_clear()
        logger.info("Analysis cache cleared")

    def test_connection(self):
        """Test the OpenAI API connection."""
        try:
            ChatCompletion = getattr(openai, 'ChatCompletion', None)
            Completion = getattr(openai, 'Completion', None)
            if ChatCompletion is not None:
                response = ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Say 'AI connected!'"}],
                    max_tokens=10
                )
                result = response.choices[0].message['content']
            elif Completion is not None:
                response = Completion.create(
                    model="gpt-4",
                    prompt="Say 'AI connected!'",
                    max_tokens=10
                )
                result = response.choices[0].text
            else:
                raise RuntimeError("No valid OpenAI completion method found.")
            return {"status": "success", "response": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
