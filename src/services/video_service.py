"""
Video service layer for managing video generation jobs.
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models.video import VideoJob, VideoConfig
from src.services.aws_service import AWSService, VideoGenerationError
from src.config.settings import config

class VideoService:
    """Manages video generation jobs and their lifecycle."""
    
    def __init__(self):
        """Initialize the video service."""
        self.aws = AWSService()
        self._jobs: List[VideoJob] = []
        self._load_existing_jobs()
        
    def create_video(self, prompt: str, duration: int, fps: int, resolution: str) -> VideoJob:
        """
        Create a new video generation job.
        
        Args:
            prompt: Text description of the video
            duration: Video duration in seconds
            fps: Frames per second
            resolution: Video resolution (e.g., '1280x720')
            
        Returns:
            VideoJob instance representing the created job
            
        Raises:
            VideoGenerationError: If job creation fails
        """
        # Create job configuration
        config = VideoConfig(
            duration=duration,
            fps=fps,
            resolution=resolution
        )
        
        # Create and initialize job
        job = VideoJob(prompt=prompt, config=config)
        
        try:
            # Start video generation
            response = self.aws.start_video_generation(job)
            job.invocation_arn = response['invocationArn']
            job.status = 'InProgress'
            
            # Save job information
            self._jobs.append(job)
            self._save_job(job)
            
            return job
            
        except VideoGenerationError as e:
            job.status = 'Failed'
            job.error_message = str(e)
            self._save_job(job)
            raise
            
    def get_job_status(self, job: VideoJob) -> str:
        """
        Get the current status of a job.
        
        Args:
            job: VideoJob instance to check
            
        Returns:
            Current status of the job
            
        Raises:
            VideoGenerationError: If status check fails
        """
        try:
            status_info = self.aws.get_job_status(job.invocation_arn)
            current_status = status_info['status']
            
            if current_status != job.status:
                job.status = current_status
                
                if current_status == 'Completed':
                    job.completed_at = datetime.now()
                    job.output_path = self.aws.download_video(job)
                elif current_status == 'Failed':
                    job.error_message = status_info.get('failureMessage', 'Unknown error')
                    
                self._save_job(job)
                
            return current_status
            
        except VideoGenerationError as e:
            job.status = 'Failed'
            job.error_message = str(e)
            self._save_job(job)
            raise
            
    def get_jobs(self) -> List[VideoJob]:
        """Get all jobs, sorted by creation time (newest first)."""
        return sorted(
            self._jobs,
            key=lambda x: x.created_at,
            reverse=True
        )
        
    def _save_job(self, job: VideoJob):
        """Save job information to disk."""
        os.makedirs(config['app'].OUTPUT_DIR, exist_ok=True)
        
        job_file = os.path.join(
            config['app'].OUTPUT_DIR,
            f'job_{job.created_at.strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        with open(job_file, 'w') as f:
            json.dump(job.to_dict(), f, indent=2)
            
    def _load_existing_jobs(self):
        """Load existing jobs from disk."""
        if not os.path.exists(config['app'].OUTPUT_DIR):
            return
            
        for file_name in os.listdir(config['app'].OUTPUT_DIR):
            if file_name.startswith('job_') and file_name.endswith('.json'):
                file_path = os.path.join(config['app'].OUTPUT_DIR, file_name)
                try:
                    with open(file_path, 'r') as f:
                        job_data = json.load(f)
                        job = VideoJob.from_dict(job_data)
                        self._jobs.append(job)
                except Exception as e:
                    print(f"Error loading job from {file_path}: {str(e)}") 