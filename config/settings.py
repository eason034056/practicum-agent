"""
Configuration Settings Module

This module manages all configuration for the Utility Identification AI Agent.
It loads environment variables and provides a centralized settings object.

Why this file exists:
- Centralized configuration management
- Type-safe access to settings
- Easy to test by mocking settings
- Prevents hardcoded values scattered throughout codebase
"""

# os: Operating system interface for file paths and environment variables
import os

# dotenv: Loads variables from .env file into environment
# load_dotenv: The function that reads .env and sets environment variables
from dotenv import load_dotenv

# pydantic: Data validation library using Python type hints
# BaseSettings: Special Pydantic class for settings management
# Field: Used to provide default values and descriptions for settings
try:
    # pydantic v2 (recommended)
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # pydantic v1 (fallback)
    from pydantic import BaseSettings, Field

# ==============================================================================
# Load Environment Variables
# ==============================================================================
# load_dotenv(): Reads the .env file and loads variables into os.environ
# This MUST be called before accessing any environment variables
# If .env file doesn't exist, it fails silently (which is fine for production)
load_dotenv()


# ==============================================================================
# Settings Class Definition
# ==============================================================================
class Settings(BaseSettings):
    """
    Application Settings
    
    This class defines all configuration parameters for the agent.
    Each field corresponds to an environment variable.
    
    Why use BaseSettings:
    - Automatic validation of types
    - Automatic loading from environment variables
    - Clear documentation of all settings in one place
    - IDE autocompletion support
    """
    
    # --------------------------------------------------------------------------
    # OpenAI Configuration
    # --------------------------------------------------------------------------
    openai_api_key: str = Field(
        # default: Value to use if environment variable is not set
        default="",
        # description: Human-readable explanation of this setting
        description="OpenAI API key for GPT models"
    )
    # Why this field: The LLM needs an API key to authenticate with OpenAI
    # Type annotation (str): Ensures the value is always a string
    # Field default (""): Prevents crash if not set, but agent won't work
    
    llm_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model name to use"
    )
    # Why "gpt-4-turbo-preview": Best balance of capability and cost
    # This model has strong reasoning abilities needed for multi-step tasks
    
    llm_temperature: float = Field(
        default=0.0,
        description="LLM temperature"
    )
    # Why float: Temperature must be a decimal number
    # Why 0.0: For factual retrieval, we want consistent, deterministic outputs
    # Higher values (1.0+) would make responses more creative but less reliable
    
    llm_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens in LLM response"
    )
    # Why int: Token counts are whole numbers
    # Why 2000: Enough for detailed responses but prevents runaway costs
    
    # --------------------------------------------------------------------------
    # Search API Configuration
    # --------------------------------------------------------------------------
    tavily_api_key: str = Field(
        default="",
        description="Tavily Search API key"
    )
    # Why Tavily: Specifically designed for LLM applications
    # Returns clean, structured results ideal for RAG
    # Alternative: Google Search API, Bing Search API
    
    google_search_api_key: str = Field(
        default="",
        description="Google Custom Search API key"
    )
    # Why Google Search: Industry-leading search quality and coverage
    # Provides official Google search results with rich metadata
    # Used for Google Search Grounding feature
    
    google_search_engine_id: str = Field(
        default="",
        description="Google Custom Search Engine ID (CX)"
    )
    # Why needed: Identifies which custom search engine to use
    # Required for Google Custom Search API authentication
    # Get from: https://programmablesearchengine.google.com/
    
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key for Grounding with Google Search"
    )
    # Why Gemini: Native Google Search grounding with automatic citations
    # Provides real-time web search integrated with Gemini models
    # Get from: https://aistudio.google.com/app/apikey
    
    # --------------------------------------------------------------------------
    # LangSmith Configuration (Monitoring)
    # --------------------------------------------------------------------------
    langchain_tracing_v2: bool = Field(
        default=True,
        description="Enable LangSmith tracing"
    )
    # Why bool: This is a yes/no flag
    # Why True: We want monitoring enabled by default for debugging
    # In production, you might set this to False to reduce overhead
    
    langchain_api_key: str = Field(
        default="",
        description="LangSmith API key"
    )
    # Why needed: Authenticates with LangSmith for trace storage
    # Traces show every step the agent takes (reasoning, tool calls, results)
    
    langchain_project: str = Field(
        default="utility-identification-agent",
        description="LangSmith project name"
    )
    # Why project name: Organizes traces for easier analysis
    # You can have multiple projects for different agents or environments
    
    # --------------------------------------------------------------------------
    # Agent Configuration
    # --------------------------------------------------------------------------
    max_iterations: int = Field(
        default=50,
        description="Maximum reasoning iterations before stopping"
    )
    # Why needed: Prevents infinite loops if agent gets confused
    # Why 50: Comprehensive utility search with Gemini grounding takes 20-40 iterations
    # (1-5. Identify AHJ, 6-15. Search each utility type with grounding, 
    #  16-30. Get detailed contact info and requirements, 31-40. Compile report)
    # Increased from 15 to support more thorough searches with Gemini
    
    enable_human_in_loop: bool = Field(
        default=False,
        description="Require human approval before tool execution"
    )
    # Why useful: Adds safety layer for critical operations
    # Why False by default: Would slow down automated usage
    # Set to True during development for transparency
    
    # --------------------------------------------------------------------------
    # Google Cloud Configuration (Optional)
    # --------------------------------------------------------------------------
    gcp_project_id: str = Field(
        default="",
        description="Google Cloud project ID"
    )
    # Why optional: Only needed for Google Cloud deployment
    # Required for: Vertex AI, Cloud Logging, Cloud Trace
    
    gcp_region: str = Field(
        default="us-central1",
        description="Google Cloud region"
    )
    # Why us-central1: Good default with broad service availability
    # Choose based on: Data residency requirements, latency, cost
    
    # --------------------------------------------------------------------------
    # Pydantic Configuration
    # --------------------------------------------------------------------------
    class Config:
        """
        Pydantic configuration for the Settings class
        
        This inner class tells Pydantic how to behave.
        """
        # env_file: Look for environment variables in this file
        env_file = ".env"
        # Why ".env": Standard convention for environment files
        
        # env_file_encoding: Character encoding for the .env file
        env_file_encoding = "utf-8"
        # Why utf-8: Universal encoding that supports all characters
        
        # case_sensitive: Whether environment variable names must match case
        case_sensitive = False
        # Why False: More forgiving (OPENAI_API_KEY = openai_api_key)
        # Prevents errors from case mismatches in .env file


# ==============================================================================
# Create Global Settings Instance
# ==============================================================================
# settings: Single global instance of Settings class
# This is the object you'll import throughout the application
settings = Settings()
# Why create instance here: 
# - Loads settings once at import time
# - All modules share the same settings object
# - Easy to mock in tests

# Usage in other files:
# from config.settings import settings
# api_key = settings.openai_api_key

