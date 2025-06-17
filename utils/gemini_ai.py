"""
Gemini AI utility functions for ResourcePro
"""
import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class GeminiAIService:
    """Service class for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.initialized = False
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.initialized = False
        else:
            logger.warning("Gemini AI not available: Missing API key or library not installed")
    
    def is_available(self) -> bool:
        """Check if Gemini AI is properly configured and available"""
        return self.initialized
    
    def generate_content(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate content using Gemini AI
        
        Args:
            prompt: The input prompt
            temperature: Controls randomness (0.0 to 1.0)
            
        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            logger.warning("Gemini AI not available")
            return None
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini AI generation failed: {e}")
            return None
    
    def generate_json_response(self, prompt: str, temperature: float = 0.3) -> Optional[Dict]:
        """
        Generate JSON response using Gemini AI
        
        Args:
            prompt: The input prompt (should request JSON format)
            temperature: Controls randomness (lower for more consistent JSON)
            
        Returns:
            Parsed JSON dict or None if failed
        """
        # Add JSON formatting instruction to prompt
        json_prompt = f"""{prompt}

IMPORTANT: Please respond with valid JSON only. Do not include any markdown formatting, explanations, or additional text outside the JSON structure."""
        
        response_text = self.generate_content(json_prompt, temperature)
        
        if not response_text:
            return None
        
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from Gemini: {e}")
            logger.error(f"Raw response: {response_text}")
            return None

# Global instance
gemini_service = GeminiAIService()
