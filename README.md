# 🎬 NovaReel Video Generator

[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

![NovaReel Logo](assets/logo.png)

A powerful and user-friendly web application for generating videos from text descriptions using Amazon Bedrock's Nova Reel model.

## Why NovaReel?

NovaReel simplifies the process of creating AI-generated videos by providing:
- 🎯 Intuitive user interface
- 🚀 Quick video generation
- 📊 Real-time job monitoring
- 🔄 Easy job management
- 🎨 Customizable video settings

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NovaReel.git
cd NovaReel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

## Usage

1. Start the application:
```bash
streamlit run src/app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter your video description and customize settings

4. Click "Generate Video" and monitor progress

## Features

- Text-to-video generation using Amazon Bedrock Nova Reel
- Customizable video parameters:
  - Duration (1-30 seconds)
  - Frame rate (24, 30, 60 fps)
  - Resolution (720p, 1080p)
- Real-time job status monitoring
- Job history tracking
- Error handling and user feedback

## Configuration

### Environment Variables

Create a `.env` file with:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
S3_BUCKET_NAME=your_bucket_name
```

### AWS Setup

1. Ensure AWS Bedrock access is enabled
2. Configure S3 bucket permissions
3. Set up appropriate IAM roles

## Development

### Project Structure

```
NovaReel/
├── src/
│   ├── app.py              # Streamlit web application
│   ├── video_job.py        # Video generation job handler
│   └── video_gen_util.py   # Core video generation utilities
├── tests/
│   └── test_video_job.py   # Unit tests
├── assets/
│   └── logo.png            # Project logo
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

### Running Tests

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 