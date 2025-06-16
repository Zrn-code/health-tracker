from google import genai
from config import get_config
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AIService:
    """AI service for health suggestions using Gemini"""
    
    def __init__(self):
        self.client = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        config = get_config()
        if config.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=config.GEMINI_API_KEY)
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"Gemini AI initialization failed: {e}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY not found - health suggestions will be disabled")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def generate_health_suggestion(self, user_data: Dict[str, Any], recent_entries: List[Dict[str, Any]]) -> str:
        """Generate health suggestion using Gemini AI"""
        if not self.client:
            raise Exception("AI service not available")
        
        try:
            context = self._build_context(user_data, recent_entries)
            prompt = self._build_prompt(context)
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Health suggestion generation failed: {e}")
            raise Exception("Failed to generate health suggestion")
    
    def _build_context(self, user_data: Dict[str, Any], recent_entries: List[Dict[str, Any]]) -> str:
        """Build context for AI prompt"""
        # Calculate age
        age = "Unknown"
        if user_data.get('birth_date'):
            birth_date = user_data['birth_date']
            if hasattr(birth_date, 'year'):
                age = datetime.now(timezone.utc).year - birth_date.year
        
        context = f"""
        User Profile:
        - Age: {age}
        - Initial Height: {user_data.get('initial_height', 'Unknown')} cm
        - Initial Weight: {user_data.get('initial_weight', 'Unknown')} kg
        
        Recent Health Data (last 7 days):
        """
        
        for entry in recent_entries:
            date_str = "Unknown"
            if entry.get('date'):
                if hasattr(entry['date'], 'date'):
                    date_str = entry['date'].date().isoformat()
                elif hasattr(entry['date'], 'isoformat'):
                    date_str = entry['date'].isoformat()
                else:
                    date_str = str(entry['date'])
            
            context += f"""
        - Date: {date_str}
        - Height: {entry.get('height', 'Unknown')} cm
        - Weight: {entry.get('weight', 'Unknown')} kg
        - Meals: Breakfast: {entry.get('breakfast', 'Unknown')}, Lunch: {entry.get('lunch', 'Unknown')}, Dinner: {entry.get('dinner', 'Unknown')}
        """
        
        return context.strip()
    
    def _build_prompt(self, context: str) -> str:
        """Build AI prompt"""
        return f"""
        {context}
        
        Based on this health data, provide a personalized, encouraging health suggestion for today. 
        Requirements:
        - Keep it concise (2-3 sentences maximum)
        - Make it actionable and specific
        - Focus on nutrition, exercise, or lifestyle improvements
        - Be positive and encouraging
        - Consider the user's recent patterns and trends
        
        Provide only the suggestion text, no additional formatting or explanation.
        """

# Global AI service instance
ai_service = AIService()
