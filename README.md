# 🎬 Nova Reel Video Generator

Generate beautiful videos from text descriptions using Amazon Bedrock's Nova Reel model.

## 🌟 Features

- 🎨 Text-to-Video Generation: Transform your text descriptions into stunning videos
- ⚙️ Customizable Settings: Control video duration, FPS, and resolution
- 📊 Real-time Status Updates: Monitor job progress with auto-refresh
- 📜 Job History: Track and manage your video generation jobs
- 🔄 Auto-refresh Status: Automatically updates job status every 10 seconds
- 🎥 Easy Download: Direct download links for completed videos
- 🔍 Job Status Tracking: Reliable status updates from AWS Bedrock
- 🏗️ Clean Architecture: Modular design with separation of concerns

## 🏗️ Project Structure

```
novareel/
├── src/                    # Source code
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── video.py      # Video and config models
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── aws_service.py    # AWS Bedrock integration
│   │   └── video_service.py  # Video generation service
│   ├── ui/                # UI components
│   │   ├── __init__.py
│   │   └── components.py  # Streamlit UI components
│   ├── config/            # Configuration
│   │   ├── __init__.py
│   │   └── settings.py    # App settings
│   └── app.py            # Main application
├── tests/                 # Test files
│   └── test_video_job.py
├── rules/                # Code quality rules
│   ├── python.mdc        # Python best practices
│   ├── clean-code.mdc    # Clean code principles
│   └── codequality.mdc   # Code quality guidelines
├── output/               # Generated videos and job data
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- AWS account with Bedrock access
- AWS credentials configured

### Installation

1. Clone the repository:
```bash
git clone https://github.com/vivek2207/novareel.git
cd novareel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS credentials and settings
```

### Running the Application

Start the Streamlit app:
```bash
python -m streamlit run src/app.py
```

The app will be available at:
- Local: http://localhost:8502
- Network: http://your-network-ip:8502

## 🎯 Usage

1. Enter your video description in the text area
2. Adjust video settings in the sidebar:
   - Duration (1-30 seconds)
   - FPS (24, 30, or 60)
   - Resolution (1280x720 or 1920x1080)
3. Click "Generate Video" to start the process
4. Monitor progress in the "Recent Jobs" section
5. Download completed videos using the provided links

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🔧 Configuration

Key settings can be adjusted in `src/config/settings.py`:
- Video duration limits
- Available FPS options
- Available resolutions
- AWS region and model settings

## 🛠️ Development

The application follows a clean architecture with:
- Models for data structures
- Services for business logic
- UI components for presentation
- Configuration for settings

### Code Quality

The project adheres to strict code quality guidelines defined in the `rules/` directory:
- Python best practices (`python.mdc`)
- Clean code principles (`clean-code.mdc`)
- Code quality standards (`codequality.mdc`)

Key principles include:
- Clear separation of concerns
- Comprehensive error handling
- Proper type hints and documentation
- Efficient AWS service integration
- Modular and maintainable UI components

## 📝 Environment Variables

Required environment variables in `.env`:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

Please ensure your code follows our quality guidelines in the `rules/` directory.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Amazon Bedrock for the Nova Reel model
- Streamlit for the web interface
- AWS SDK for Python (Boto3)
- The open-source community for inspiration and tools 