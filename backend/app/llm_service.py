"""
LLM service for generating job proposals
Supports Groq and HuggingFace APIs
"""
import logging
import os
import random
import time
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating proposals using LLM APIs"""
    
    MY_PROFILE = """
I am an AI & Software Engineer with 1.5+ years of experience building production AI systems.

Key expertise:
- Full-stack development: Python/FastAPI and React
- AI/ML: Machine Learning, NLP, Computer Vision
- Automation systems that save 25-30 hours per day
- Experience with Odoo ERP systems
- Production-ready AI applications

I deliver high-quality, scalable solutions and excel at understanding complex requirements.
"""
    
    TONE_VARIANTS = [
        "confident_direct",
        "enthusiastic_professional", 
        "experienced_consultative"
    ]
    
    def __init__(self, api_key: str, provider: str = "groq"):
        """
        Initialize LLM service
        
        Args:
            api_key: API key for the LLM provider
            provider: Either 'groq' or 'huggingface'
        """
        self.api_key = api_key
        self.provider = provider.lower()
        self.max_retries = 3
        self.base_backoff = 2  # seconds
        
        if self.provider == "groq":
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-70b-versatile"
        elif self.provider == "huggingface":
            self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
            self.model = "mixtral"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"Initialized LLM service with provider: {provider}")
    
    def _build_prompt(self, job_description: str, job_title: str, tone: str) -> str:
        """Build prompt for proposal generation"""
        
        tone_instructions = {
            "confident_direct": "Write in a confident, direct tone. Be assertive about your capabilities.",
            "enthusiastic_professional": "Write with enthusiasm and energy while maintaining professionalism.",
            "experienced_consultative": "Write from an experienced consultant perspective, showing deep expertise."
        }
        
        prompt = f"""Generate a personalized job proposal based on the following:

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description}

MY PROFILE:
{self.MY_PROFILE}

REQUIREMENTS:
- Maximum 180 words
- {tone_instructions.get(tone, tone_instructions['confident_direct'])}
- Mention ONE specific detail from the job description that shows you read it carefully
- Show relevant experience
- No emojis or excessive punctuation
- No generic statements
- Be concise and impactful
- End with a clear call to action

Write the proposal now:"""
        
        return prompt
    
    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional proposal writer for freelance job applications. Write compelling, personalized proposals."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 400,
            "top_p": 0.9
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    def _call_huggingface(self, prompt: str) -> Optional[str]:
        """Call HuggingFace API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 400,
                "temperature": 0.8,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        return None
    
    def generate_proposal(self, job_description: str, job_title: str, 
                         retry_count: int = 0) -> Optional[str]:
        """
        Generate proposal for a job
        
        Args:
            job_description: Full job description
            job_title: Job title
            retry_count: Current retry attempt (internal use)
            
        Returns:
            Generated proposal text or None if failed
        """
        try:
            # Select random tone for variety
            tone = random.choice(self.TONE_VARIANTS)
            
            # Build prompt
            prompt = self._build_prompt(job_description, job_title, tone)
            
            # Call appropriate API
            if self.provider == "groq":
                proposal = self._call_groq(prompt)
            else:
                proposal = self._call_huggingface(prompt)
            
            if proposal:
                # Validate length (approximately)
                word_count = len(proposal.split())
                if word_count > 220:
                    logger.warning(f"Proposal too long ({word_count} words), truncating...")
                    words = proposal.split()[:180]
                    proposal = " ".join(words)
                
                logger.info(f"Successfully generated proposal ({len(proposal.split())} words)")
                return proposal
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            
            # Retry with exponential backoff
            if retry_count < self.max_retries:
                backoff_time = self.base_backoff ** (retry_count + 1)
                logger.info(f"Retrying in {backoff_time} seconds... (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(backoff_time)
                return self.generate_proposal(job_description, job_title, retry_count + 1)
            
            logger.error(f"Failed to generate proposal after {self.max_retries} retries")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error generating proposal: {e}")
            return None
    
    def generate_proposal_with_variability(self, job_description: str, 
                                          job_title: str) -> Optional[str]:
        """
        Generate proposal with added variability
        Tries different tones if first attempt seems generic
        """
        proposal = self.generate_proposal(job_description, job_title)
        
        # Simple check for generic content
        if proposal:
            generic_phrases = ["i am writing", "i am interested", "dear hiring manager"]
            is_generic = any(phrase in proposal.lower() for phrase in generic_phrases)
            
            if is_generic:
                logger.info("Detected generic proposal, regenerating...")
                proposal = self.generate_proposal(job_description, job_title)
        
        return proposal
