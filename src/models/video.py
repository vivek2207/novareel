"""
Data models for video generation.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional
import random

@dataclass
class VideoConfig:
    """Configuration for video generation."""
    duration: int
    fps: int
    resolution: str
    seed: int = None

    def __post_init__(self):
        """Initialize seed if not provided."""
        if self.seed is None:
            self.seed = random.randint(0, 2147483646)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format for API."""
        return {
            'durationSeconds': self.duration,
            'fps': self.fps,
            'dimension': self.resolution,
            'seed': self.seed
        }

@dataclass
class VideoJob:
    """Represents a video generation job."""
    prompt: str
    config: VideoConfig
    invocation_arn: Optional[str] = None
    status: str = 'Pending'
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary format for storage."""
        return {
            'prompt': self.prompt,
            'config': {
                'duration': self.config.duration,
                'fps': self.config.fps,
                'resolution': self.config.resolution,
                'seed': self.config.seed
            },
            'invocation_arn': self.invocation_arn,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'output_path': self.output_path,
            'error_message': self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoJob':
        """Create a VideoJob instance from dictionary data."""
        # Handle old format where invocation_arn was in response
        if 'response' in data and 'invocationArn' in data['response']:
            invocation_arn = data['response']['invocationArn']
        else:
            invocation_arn = data.get('invocation_arn')

        # Handle old format where config used different keys
        config_data = data['config']
        if 'durationSeconds' in config_data:
            duration = config_data['durationSeconds']
            resolution = config_data['dimension']
        else:
            duration = config_data['duration']
            resolution = config_data['resolution']

        config = VideoConfig(
            duration=duration,
            fps=config_data['fps'],
            resolution=resolution,
            seed=config_data.get('seed')
        )

        return cls(
            prompt=data['prompt'],
            config=config,
            invocation_arn=invocation_arn,
            status=data.get('status', 'InProgress'),  # Default to InProgress for old format
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            output_path=data.get('output_path'),
            error_message=data.get('error_message')
        ) 