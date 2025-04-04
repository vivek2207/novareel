"""
Tests for video job functionality
"""

import unittest
from datetime import datetime

from src.models.video import VideoJob, VideoConfig

class TestVideoJob(unittest.TestCase):
    """Test cases for VideoJob class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = VideoConfig(
            duration=5,
            fps=30,
            resolution="1280x720"
        )
        
        self.job = VideoJob(
            prompt="Test video",
            config=self.config,
            invocation_arn="test_arn",
            created_at=datetime.now(),
            status="InProgress"
        )
    
    def test_job_creation(self):
        """Test video job creation."""
        self.assertEqual(self.job.prompt, "Test video")
        self.assertEqual(self.job.status, "InProgress")
        self.assertEqual(self.job.config.duration, 5)
        self.assertEqual(self.job.config.fps, 30)
        self.assertEqual(self.job.config.resolution, "1280x720")
    
    def test_job_to_dict(self):
        """Test conversion of job to dictionary."""
        job_dict = self.job.to_dict()
        self.assertEqual(job_dict["prompt"], "Test video")
        self.assertEqual(job_dict["status"], "InProgress")
        self.assertEqual(job_dict["config"]["duration"], 5)
        self.assertEqual(job_dict["config"]["fps"], 30)
        self.assertEqual(job_dict["config"]["resolution"], "1280x720")
    
    def test_job_from_dict(self):
        """Test creation of job from dictionary."""
        job_dict = {
            "prompt": "Test video",
            "config": {
                "duration": 5,
                "fps": 30,
                "resolution": "1280x720"
            },
            "invocation_arn": "test_arn",
            "created_at": datetime.now().isoformat(),
            "status": "InProgress"
        }
        
        job = VideoJob.from_dict(job_dict)
        self.assertEqual(job.prompt, "Test video")
        self.assertEqual(job.status, "InProgress")
        self.assertEqual(job.config.duration, 5)
        self.assertEqual(job.config.fps, 30)
        self.assertEqual(job.config.resolution, "1280x720") 