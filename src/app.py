"""
Main application file for the Nova Reel Video Generator.
"""

import streamlit as st
from typing import Optional

from src.services.video_service import VideoService, VideoGenerationError
from src.ui.components import VideoSettingsUI, JobHistoryUI, MainUI

class NovaReelApp:
    """Main application class for Nova Reel Video Generator."""
    
    def __init__(self):
        """Initialize the application."""
        self.video_service = VideoService()
        self._setup_page()
        
    def _setup_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Nova Reel Video Generator",
            page_icon="🎬",
            layout="wide"
        )
        
    def run(self):
        """Run the application."""
        # Get video settings from sidebar
        config = VideoSettingsUI.render()
        
        # Render main content area
        prompt, should_generate = MainUI.render()
        
        # Handle video generation
        if should_generate:
            with st.spinner("Initializing video generation..."):
                try:
                    job = self.video_service.create_video(
                        prompt=prompt,
                        duration=config.duration,
                        fps=config.fps,
                        resolution=config.resolution
                    )
                    st.success("Video generation started successfully!")
                    
                except VideoGenerationError as e:
                    st.error(f"Error starting video generation: {str(e)}")
                    
        # Display job history with auto-refresh
        JobHistoryUI.render(
            jobs=self.video_service.get_jobs(),
            video_service=self.video_service
        )
        
        # Add footer
        st.markdown("---")
        st.markdown("Made with ❤️ using Amazon Bedrock Nova Reel")

def main():
    """Application entry point."""
    app = NovaReelApp()
    app.run()

if __name__ == "__main__":
    main() 