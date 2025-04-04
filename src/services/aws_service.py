"""
AWS service layer for interacting with AWS services.
"""

from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
import os

from src.config.settings import config
from src.models.video import VideoJob

class AWSError(Exception):
    """Base exception for AWS-related errors."""
    pass

class VideoGenerationError(AWSError):
    """Exception raised for errors during video generation."""
    pass

class AWSService:
    """Handles interactions with AWS services."""
    
    def __init__(self):
        """Initialize AWS clients."""
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=config['aws'].REGION)
        self.s3 = boto3.client('s3', region_name=config['aws'].REGION)
        
    def start_video_generation(self, job: VideoJob) -> Dict[str, Any]:
        """
        Start an async video generation job.
        
        Args:
            job: VideoJob instance containing generation parameters
            
        Returns:
            Dict containing the response from AWS Bedrock
            
        Raises:
            VideoGenerationError: If the API call fails
        """
        try:
            response = self.bedrock_runtime.start_async_invoke(
                modelId=config['aws'].MODEL_ID,
                modelInput=self._prepare_model_input(job),
                outputDataConfig=self._get_output_config()
            )
            return response
        except ClientError as e:
            raise VideoGenerationError(f"AWS API Error: {str(e)}")
            
    def get_job_status(self, invocation_arn: str) -> Dict[str, Any]:
        """
        Get the status of an async job.
        
        Args:
            invocation_arn: The ARN of the async invocation
            
        Returns:
            Dict containing the job status information
            
        Raises:
            VideoGenerationError: If the status check fails
        """
        try:
            # First check completed jobs
            completed_jobs = self.bedrock_runtime.list_async_invokes(statusEquals="Completed")
            for job in completed_jobs.get('asyncInvokeSummaries', []):
                if job['invocationArn'] == invocation_arn:
                    return {
                        'status': 'Completed',
                        'outputDataConfig': {
                            's3OutputDataConfig': {
                                's3Uri': f"s3://{config['aws'].BUCKET_NAME}"
                            }
                        }
                    }

            # Then check failed jobs
            failed_jobs = self.bedrock_runtime.list_async_invokes(statusEquals="Failed")
            for job in failed_jobs.get('asyncInvokeSummaries', []):
                if job['invocationArn'] == invocation_arn:
                    return {
                        'status': 'Failed',
                        'failureMessage': job.get('failureReason', 'Unknown error')
                    }

            # If not found in completed or failed, try direct status check
            try:
                return self.bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
            except ClientError as e:
                if 'ResourceNotFoundException' in str(e):
                    # If not found but we know it exists, assume it's completed
                    # (since we already checked failed jobs)
                    return {
                        'status': 'Completed',
                        'outputDataConfig': {
                            's3OutputDataConfig': {
                                's3Uri': f"s3://{config['aws'].BUCKET_NAME}"
                            }
                        }
                    }
                raise

        except ClientError as e:
            raise VideoGenerationError(f"Error checking job status: {str(e)}")
            
    def download_video(self, job: VideoJob) -> Optional[str]:
        """
        Download the generated video from S3.
        
        Args:
            job: VideoJob instance containing the job information
            
        Returns:
            Path to the downloaded video file, or None if not found
            
        Raises:
            VideoGenerationError: If the download fails
        """
        try:
            invocation_id = job.invocation_arn.split("/")[-1]
            # Create job-specific directory
            job_dir = f"{config['app'].OUTPUT_DIR}/{invocation_id}"
            os.makedirs(job_dir, exist_ok=True)
            
            local_file = f"{job_dir}/output.mp4"
            
            # Check if video already downloaded
            if os.path.exists(local_file):
                return local_file
                
            # The expected path in S3 is {invocation_id}/output.mp4
            s3_key = f"{invocation_id}/output.mp4"
            
            try:
                # Try to download directly if we know the exact path
                self.s3.download_file(
                    config['aws'].BUCKET_NAME,
                    s3_key,
                    local_file
                )
                return local_file
            except ClientError:
                # If direct path fails, try listing objects to find the file
                response = self.s3.list_objects_v2(
                    Bucket=config['aws'].BUCKET_NAME,
                    Prefix=invocation_id
                )
                
                # Find and download the first MP4 file
                for obj in response.get("Contents", []):
                    if obj["Key"].endswith(".mp4"):
                        self.s3.download_file(
                            config['aws'].BUCKET_NAME,
                            obj["Key"],
                            local_file
                        )
                        return local_file
            
            return None
            
        except ClientError as e:
            raise VideoGenerationError(f"Error downloading video: {str(e)}")
            
    def _prepare_model_input(self, job: VideoJob) -> Dict[str, Any]:
        """Prepare the input for the Bedrock model."""
        return {
            "taskType": "TEXT_VIDEO",
            "textToVideoParams": {
                "text": job.prompt
            },
            "videoGenerationConfig": job.config.to_dict()
        }
        
    def _get_output_config(self) -> Dict[str, Any]:
        """Get the S3 output configuration."""
        return {
            "s3OutputDataConfig": {
                "s3Uri": f"s3://{config['aws'].BUCKET_NAME}"
            }
        } 