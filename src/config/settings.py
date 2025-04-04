"""
Configuration settings for the Nova Reel application.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class AWSConfig:
    """AWS-specific configuration settings."""
    BUCKET_NAME: str = 'vpc-reaserch'
    MODEL_ID: str = 'amazon.nova-reel-v1:0'
    REGION: str = 'us-east-1'

@dataclass(frozen=True)
class AppConfig:
    """Application-specific configuration settings."""
    OUTPUT_DIR: str = 'output'
    DEFAULT_FPS: int = 24
    DEFAULT_DURATION: int = 6
    DEFAULT_RESOLUTION: str = '1280x720'
    MAX_DURATION: int = 30
    MIN_DURATION: int = 1
    AVAILABLE_FPS: list[int] = (24, 30, 60)
    AVAILABLE_RESOLUTIONS: list[str] = ('1280x720', '1920x1080')

# Global configuration object
config = {
    'aws': AWSConfig(),
    'app': AppConfig()
} 