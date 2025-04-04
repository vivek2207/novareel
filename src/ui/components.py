"""
UI components for the Streamlit interface.
"""

import streamlit as st
from typing import List, Tuple
from datetime import datetime
import time

from src.models.video import VideoConfig, VideoJob
from src.config.settings import config
from src.services.video_service import VideoService

class VideoSettingsUI:
    """UI component for video generation settings."""
    
    @staticmethod
    def render() -> VideoConfig:
        """
        Render video settings controls.
        
        Returns:
            VideoConfig instance with user-selected settings
        """
        st.sidebar.header("Video Settings")
        
        duration = st.sidebar.slider(
            "Duration (seconds)",
            min_value=config['app'].MIN_DURATION,
            max_value=config['app'].MAX_DURATION,
            value=config['app'].DEFAULT_DURATION,
            help="Length of the generated video in seconds"
        )
        
        fps = st.sidebar.selectbox(
            "Frames Per Second",
            options=config['app'].AVAILABLE_FPS,
            index=0,
            help="Number of frames per second"
        )
        
        resolution = st.sidebar.selectbox(
            "Resolution",
            options=config['app'].AVAILABLE_RESOLUTIONS,
            index=0,
            help="Video resolution (width x height)"
        )
        
        return VideoConfig(
            duration=duration,
            fps=fps,
            resolution=resolution
        )

class JobHistoryUI:
    """UI component for displaying job history."""
    
    @staticmethod
    def render(jobs: List[VideoJob], video_service: VideoService):
        """
        Render job history section.
        
        Args:
            jobs: List of VideoJob instances to display
            video_service: VideoService instance for status updates
        """
        if not jobs:
            return
            
        # Initialize session state for refresh timestamps if not exists
        if 'job_refresh_times' not in st.session_state:
            st.session_state.job_refresh_times = {}
            
        st.markdown("---")
        
        # Sort jobs by created_at timestamp (newest first)
        sorted_jobs = sorted(jobs, key=lambda x: x.created_at, reverse=True)
        
        # Split jobs into recent (5 most recent) and archived (the rest)
        recent_jobs = sorted_jobs[:5]
        archived_jobs = sorted_jobs[5:] if len(sorted_jobs) > 5 else []
        
        # Create tabs for recent and archived jobs
        recent_tab, archive_tab = st.tabs(["Recent Jobs", f"Archive ({len(archived_jobs)} jobs)"])
        
        # Display recent jobs
        with recent_tab:
            for idx, job in enumerate(recent_jobs):
                with st.expander(
                    f"Job {idx + 1}: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {job.prompt[:50]}...",
                    expanded=(idx == 0)
                ):
                    JobHistoryUI._render_job_details(job, video_service)
        
        # Display archived jobs
        with archive_tab:
            if archived_jobs:
                st.info(f"Showing {len(archived_jobs)} older jobs")
                for idx, job in enumerate(archived_jobs):
                    with st.expander(
                        f"Job {idx + 6}: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {job.prompt[:50]}...",
                        expanded=False
                    ):
                        JobHistoryUI._render_job_details(job, video_service)
            else:
                st.info("No archived jobs available yet")
        
    @staticmethod
    def _render_job_details(job: VideoJob, video_service: VideoService):
        """Render details for a single job."""
        st.write("**Prompt:**", job.prompt)
        st.write("**Configuration:**")
        st.json(job.config.to_dict())
        
        # Status section
        status_col, refresh_col = st.columns([3, 1])
        
        with status_col:
            # Check if we need to refresh the status
            current_time = time.time()
            last_refresh = st.session_state.job_refresh_times.get(job.invocation_arn, 0)
            
            if job.status == 'InProgress' and (current_time - last_refresh) >= 10:
                try:
                    video_service.get_job_status(job)
                    st.session_state.job_refresh_times[job.invocation_arn] = current_time
                except Exception as e:
                    st.error(f"Error updating status: {str(e)}")
            
            # Display status
            if job.status == 'Completed':
                st.success("✅ Completed")
                if job.output_path:
                    # Display both a download link and the video player
                    st.markdown(f"🎥 [Download Video]({job.output_path})")
                    
                    # Display video directly in the app
                    st.video(job.output_path)
                    
                    # Show job ID for reference
                    job_id = job.invocation_arn.split('/')[-1]
                    st.info(f"Job ID: {job_id}")
                    
                    # Show S3 path
                    s3_path = f"s3://{config['aws'].BUCKET_NAME}/{job_id}/output.mp4"
                    st.text(f"S3 Path: {s3_path}")
            elif job.status == 'Failed':
                st.error(f"❌ Failed: {job.error_message or 'Unknown error'}")
            else:
                st.info("⏳ In Progress")
                st.progress(0.5, "Generating video...")
        
        with refresh_col:
            if st.button("🔄 Refresh", key=f"refresh_{job.invocation_arn}_{time.time()}"):
                try:
                    video_service.get_job_status(job)
                    st.session_state.job_refresh_times[job.invocation_arn] = current_time
                    st.rerun()
                except Exception as e:
                    st.error(f"Error refreshing status: {str(e)}")

class MainUI:
    """Main UI component."""
    
    @staticmethod
    def render() -> Tuple[str, bool]:
        """
        Render main content area.
        
        Returns:
            Tuple of (prompt, should_generate)
        """
        st.title("🎬 Nova Reel Video Generator")
        st.markdown("""
        Generate beautiful videos from text descriptions using Amazon Bedrock's Nova Reel model.
        Simply enter your prompt and customize the video settings below.
        """)
        
        prompt = st.text_area(
            "Enter your video description",
            placeholder="Example: A beautiful sunset over a mountain lake...",
            help="Describe the video you want to generate"
        )
        
        should_generate = st.button(
            "Generate Video",
            type="primary",
            disabled=not prompt
        )
        
        return prompt, should_generate 