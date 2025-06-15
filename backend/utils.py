from google import genai
from config import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self.initialize_gemini()
    
    def initialize_gemini(self):
        """Initialize Gemini AI client"""
        if Config.GEMINI_API_KEY:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            logger.info("Gemini AI initialized successfully")
        else:
            logger.warning("GEMINI_API_KEY not found - health suggestions will be disabled")
    
    def is_available(self):
        """Check if AI service is available"""
        return self.client is not None
    
    def generate_health_suggestion(self, user_data, recent_entries):
        """Generate health suggestion using Gemini AI"""
        if not self.client:
            raise Exception("AI service not available")
        
        context = self._build_context(user_data, recent_entries)
        prompt = f"""
        {context}
        
        Based on this health data, provide a personalized, encouraging health suggestion for today. 
        Keep it concise (2-3 sentences), actionable, and positive. Focus on nutrition, exercise, or lifestyle tips.
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    
    def _build_context(self, user_data, recent_entries):
        """Build context for AI prompt"""
        context = f"""
        User Profile:
        - Age: {datetime.utcnow().year - user_data.get('birth_date', datetime.utcnow()).year if user_data.get('birth_date') else 'Unknown'}
        - Initial Height: {user_data.get('initial_height', 'Unknown')} cm
        - Initial Weight: {user_data.get('initial_weight', 'Unknown')} kg
        
        Recent Entries (last 7 days):
        """
        
        for entry in recent_entries:
            entry_data = entry.to_dict()
            context += f"""
        - Date: {entry_data.get('date', 'Unknown')}
        - Height: {entry_data.get('height', 'Unknown')} cm
        - Weight: {entry_data.get('weight', 'Unknown')} kg
        - Meals: Breakfast: {entry_data.get('breakfast', 'Unknown')}, Lunch: {entry_data.get('lunch', 'Unknown')}, Dinner: {entry_data.get('dinner', 'Unknown')}
        """
        return context

# Global AI service instance
ai_service = AIService()
