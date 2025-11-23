"""
LLM Client - Groq Only
Supports Groq LLM provider for data extraction.
API key is loaded from environment variables via .env file.
"""

from typing import List, Dict, Any, Optional
from groq import Groq
from utils.logger import logger
from config.llm_config import (
    get_primary_model,
    get_model_config,
    get_current_priority,
    GROQ_CONFIG
)
from config.settings import settings

class LLMClient:
    """LLM Client for Groq API"""
    
    def __init__(self):
        """Initialize LLM client with Groq"""
        self.primary_model = get_primary_model()
        self.model_priority = get_current_priority()
        self.groq_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client"""
        try:
            # Initialize Groq client with API key from environment variables
            if settings.GROQ_API_KEY:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("✅ Groq client initialized successfully")
            else:
                logger.warning("⚠️ GROQ_API_KEY not found in environment variables")
                logger.warning("⚠️ Please set GROQ_API_KEY in your .env file")
        except Exception as e:
            logger.error(f"❌ Error initializing Groq client: {e}")
            raise
    
    def _call_groq(self, messages: List[Dict[str, str]], config: Dict[str, Any]) -> str:
        """
        Call Groq API to generate response
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            config: Configuration dictionary with model parameters
            
        Returns:
            Generated response text from Groq API
        """
        try:
            if not self.groq_client:
                raise Exception("Groq client not initialized. Check GROQ_API_KEY in .env file")
            
            response = self.groq_client.chat.completions.create(
                model=config["model"],
                messages=messages,
                temperature=config.get("temperature", 0.3),
                max_tokens=config.get("max_tokens", 8000),
                top_p=config.get("top_p", 0.8)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {e}")
            raise
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> str:
        """
        Generate response using Groq LLM
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt for context
            model_name: Optional specific model to use (defaults to GROQ)
        
        Returns:
            Generated response text from Groq API
            
        Raises:
            Exception: If API call fails or client not initialized
        """
        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Use specific model if provided, otherwise use primary model
        if model_name:
            models_to_try = [model_name]
        else:
            models_to_try = self.model_priority
        
        # Try each model in priority order (only Groq for now)
        last_error = None
        for model_name in models_to_try:
            try:
                config = get_model_config(model_name)
                if not config:
                    logger.warning(f"⚠️ Model config not found: {model_name}")
                    continue
                
                logger.info(f"🔄 Calling Groq API with model: {config['model']}")
                
                if model_name == "GROQ":
                    result = self._call_groq(messages, config)
                else:
                    logger.warning(f"⚠️ Unknown model: {model_name}. Only GROQ is supported.")
                    continue
                
                logger.info(f"✅ Successfully generated response using {model_name}")
                return result
                
            except Exception as e:
                last_error = e
                logger.error(f"❌ Model {model_name} failed: {e}")
                # Since we only have Groq, don't try other models
                break
        
        # All models failed
        error_msg = f"❌ LLM generation failed. Error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

# Global LLM client instance
llm_client = LLMClient()

__all__ = ["LLMClient", "llm_client"]
