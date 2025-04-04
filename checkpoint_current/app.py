"""
Streamlit web application for Nova Reel video generation.
"""

import streamlit as st
import json
import time
from video_job import VideoJob

# Page config
st.set_page_config(
    page_title="Nova Reel Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 Nova Reel Video Generator")
st.markdown("""
Generate beautiful videos from text descriptions using Amazon Bedrock's Nova Reel model.
Simply enter your prompt and customize the video settings below.
""")

# Sidebar for video settings
st.sidebar.header("Video Settings")

duration = st.sidebar.slider(
    "Duration (seconds)",
    min_value=1,
    max_value=30,
    value=6,
    help="Length of the generated video in seconds"
)

fps = st.sidebar.selectbox(
    "Frames Per Second",
    options=[24, 30, 60],
    index=0,
    help="Number of frames per second"
)

resolution = st.sidebar.selectbox(
    "Resolution",
    options=["1280x720", "1920x1080"],
    index=0,
    help="Video resolution (width x height)"
)

# Main content area
prompt = st.text_area(
    "Enter your video description",
    placeholder="Example: A beautiful sunset over a mountain lake, with golden clouds reflecting in the calm water",
    help="Describe the video you want to generate"
)

# Job history section
if 'job_history' not in st.session_state:
    st.session_state.job_history = []

# Generate button
if st.button("Generate Video", type="primary", disabled=not prompt):
    with st.spinner("Initializing video generation..."):
        try:
            # Create video job
            job = VideoJob()
            result = job.create_video(
                prompt=prompt,
                duration=duration,
                fps=fps,
                resolution=resolution
            )
            
            # Add to job history
            job_info = {
                'prompt': prompt,
                'invocation_arn': result['response']['invocationArn'],
                'status': 'In Progress',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'config': result['config']
            }
            st.session_state.job_history.insert(0, job_info)
            
            st.success("Video generation started successfully!")
            
        except Exception as e:
            st.error(f"Error starting video generation: {str(e)}")

# Job monitoring section
if st.session_state.job_history:
    st.markdown("---")
    st.header("Recent Jobs")
    
    for idx, job_info in enumerate(st.session_state.job_history):
        with st.expander(f"Job {idx + 1}: {job_info['timestamp']}", expanded=(idx == 0)):
            # Display job details
            st.write("**Prompt:**", job_info['prompt'])
            st.write("**Configuration:**")
            st.json(job_info['config'])
            
            # Status checking
            status_col, refresh_col = st.columns([3, 1])
            with status_col:
                if job_info['status'] != 'Completed' and job_info['status'] != 'Failed':
                    try:
                        job = VideoJob()
                        status_info = job.get_job_status(job_info['invocation_arn'])
                        current_status = status_info['status']
                        
                        if current_status == "Completed":
                            bucket_uri = status_info['outputDataConfig']['s3OutputDataConfig']['s3Uri']
                            video_path = f"{bucket_uri}/{job_info['invocation_arn'].split('/')[-1]}/output.mp4"
                            st.success(f"Video generation completed! Available at: {video_path}")
                            job_info['status'] = 'Completed'
                            job_info['video_path'] = video_path
                        elif current_status == "Failed":
                            failure_message = status_info.get('failureMessage', 'Unknown error')
                            st.error(f"Video generation failed: {failure_message}")
                            job_info['status'] = 'Failed'
                        else:
                            st.info("Status: In Progress")
                            
                    except Exception as e:
                        st.error(f"Error checking status: {str(e)}")
                elif job_info['status'] == 'Completed':
                    st.success(f"Video available at: {job_info['video_path']}")
                else:
                    st.error("Job failed")
            
            with refresh_col:
                if st.button("Refresh", key=f"refresh_{idx}_{time.time()}"):
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Amazon Bedrock Nova Reel") 