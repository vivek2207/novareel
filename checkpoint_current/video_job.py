"""
Video generation job handler for Nova Reel application.
Uses video_gen_util.py for core functionality.
"""

import boto3
import json
import time
import os
import sys
import random
from typing import Dict, Any, Optional, List

# Add parent directory to Python path to import video_gen_util
from video_gen_util import (
    save_invocation_info,
    monitor_and_download_videos,
    download_video_for_invocation_arn,
    get_job_id_from_arn
)

# Constants
BUCKET_NAME = 'vpc-reaserch'
MODEL_ID = 'amazon.nova-reel-v1:0'
OUTPUT_DIR = 'output'
DEFAULT_DURATION = 6
DEFAULT_FPS = 24
DEFAULT_DIMENSION = {"width": 1280, "height": 720}

class VideoJob:
    """Handles video generation jobs using Amazon Bedrock Nova Reel."""
    
    def __init__(self):
        """Initialize the Bedrock runtime client."""
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        
    def create_video(self, prompt: str, duration: int = 6, fps: int = 24, resolution: str = '1280x720') -> Dict[str, Any]:
        """
        Creates a video using the Nova Reel model.
        
        Args:
            prompt (str): The text description for video generation
            duration (int): Video duration in seconds
            fps (int): Frames per second
            resolution (str): Video resolution
            
        Returns:
            Dict[str, Any]: Response containing job information
            
        Raises:
            ValidationException: If the input parameters are invalid
        """
        # Generate a random seed for unique results
        seed = random.randint(0, 2147483646)
        
        # Prepare the model input
        model_input = {
            "taskType": "TEXT_VIDEO",
            "textToVideoParams": {
                "text": prompt
            },
            "videoGenerationConfig": {
                "durationSeconds": duration,
                "fps": fps,
                "dimension": resolution,
                "seed": seed
            }
        }
        
        try:
            # Start async video generation
            response = self.bedrock_runtime.start_async_invoke(
                modelId=MODEL_ID,
                modelInput=model_input,
                outputDataConfig={
                    "s3OutputDataConfig": {
                        "s3Uri": f"s3://{BUCKET_NAME}"
                    }
                }
            )
            
            # Save job information
            job_info = {
                'prompt': prompt,
                'config': {
                    'duration': duration,
                    'fps': fps,
                    'resolution': resolution,
                    'seed': seed
                },
                'response': response
            }
            
            # Create output directory if it doesn't exist
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Save job info to file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            job_file = os.path.join(OUTPUT_DIR, f'job_{timestamp}.json')
            with open(job_file, 'w') as f:
                json.dump(job_info, f, indent=2)
            
            return job_info
            
        except Exception as e:
            raise Exception(f"Error creating video: {str(e)}")
            
    def get_job_status(self, invocation_arn: str) -> Dict[str, Any]:
        """
        Get the status of a video generation job.
        
        Args:
            invocation_arn (str): The ARN of the async invocation to check
            
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            return self.bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
        except Exception as e:
            raise Exception(f"Error checking job status: {str(e)}")

def main():
    """Example usage of VideoJob class."""
    # Create a video job
    job = VideoJob()
    
    # Example prompt
    prompt = "A beautiful sunset over a mountain lake, with golden clouds reflecting in the calm water"
    
    try:
        # Start video generation
        print(f"Creating video for prompt: {prompt}")
        result = job.create_video(prompt)
        
        print("\nJob started successfully!")
        print(json.dumps(result, indent=2))
        
        # Get the invocation ARN
        invocation_arn = result['response']['invocationArn']
        print(f"\nInvocation ARN: {invocation_arn}")
        
        # Poll for job completion
        print("\nPolling for job completion...")
        while True:
            status_info = job.get_job_status(invocation_arn)
            status = status_info['status']
            
            if status == "Completed":
                bucket_uri = status_info['outputDataConfig']['s3OutputDataConfig']['s3Uri']
                print(f"\nSuccess! Video is available at: {bucket_uri}/output.mp4")
                break
            elif status == "Failed":
                failure_message = status_info.get('failureMessage', 'Unknown error')
                print(f"\nVideo generation failed: {failure_message}")
                break
            else:
                print("In progress. Waiting 15 seconds...")
                time.sleep(15)
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_create_video():
    # Test video creation with valid parameters
    ...

def test_monitor_job_status():
    # Test job status monitoring
    ...

if __name__ == "__main__":
    main() 