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
        st.header("Recent Jobs")
        
        # Display jobs in reverse chronological order
        for idx, job in enumerate(reversed(jobs)):
            with st.expander(
                f"Job {len(jobs) - idx}: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {job.prompt[:50]}...",
                expanded=(idx == 0)
            ):
                JobHistoryUI._render_job_details(job, video_service)
                
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
                    st.markdown(f"🎥 [Download Video]({job.output_path})")
            elif job.status == 'Failed':
                st.error(f"❌ Failed: {job.error_message or 'Unknown error'}")
            else:
                st.info("⏳ In Progress")
                st.progress(0.5, "Generating video...")
        
        with refresh_col:
            if st.button("🔄 Refresh", key=f"refresh_{job.invocation_arn}"):
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