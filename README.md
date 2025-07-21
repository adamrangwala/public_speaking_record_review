# Public Speaking Coach MVP

A web application that helps users analyze their public speaking by uploading videos and getting feedback through three different viewing modes.

## Features

- **Video Upload**: Drag & drop MP4 files (up to 50MB)
- **Three Analysis Views**:
  - 🎥 **Video View**: Watch your presentation with guided prompts for body language analysis
  - 🎵 **Audio View**: Listen to audio with basic waveform visualization
  - 📝 **Text View**: Manual transcript input with content analysis prompts
- **Notes System**: Guided prompts for each view with persistent storage
- **Report Generation**: Combined analysis report with copy-to-clipboard functionality
- **Modern UI**: Instagram-inspired design with Tailwind CSS and Alpine.js

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, Tailwind CSS, Alpine.js
- **Database**: SQLite
- **Video Processing**: MoviePy (with graceful fallback)
- **Audio Processing**: Librosa (with graceful fallback)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd public_speaking_record_review
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

6. **Open your browser** and navigate to: `http://127.0.0.1:8000`

## Project Structure

```
public_speaking_record_review/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # SQLAlchemy setup and connection
│   ├── models.py               # Database models (Videos, Notes, Prompts)
│   ├── routes/                 # Route modules (future expansion)
│   ├── utils/
│   │   ├── file_validation.py  # Upload validation logic
│   │   └── video_processing.py # Video/audio processing utilities
│   ├── static/
│   │   ├── css/styles.css      # Custom styles
│   │   ├── js/app.js           # Custom JavaScript
│   │   └── uploads/            # Uploaded video storage
│   └── templates/
│       ├── base.html           # Base template
│       ├── index.html          # Homepage with upload
│       ├── analysis.html       # Three-view analysis page
│       └── report.html         # Combined report view
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database (auto-created)
└── README.md                   # This file
```

## Usage

1. **Upload Video**: 
   - Visit the homepage
   - Drag & drop an MP4 file or click "Choose File"
   - File must be MP4 format and under 50MB

2. **Analyze Video**:
   - After upload, you'll be redirected to the analysis page
   - Switch between three tabs: Video, Audio, and Text
   - Answer guided prompts in each view
   - Notes are automatically saved as you type

3. **Generate Report**:
   - Click "View Report" to see all your analysis combined
   - Copy report to clipboard or print
   - Navigate back to analysis or upload new video

## API Endpoints

- `GET /` - Homepage with upload form
- `POST /upload` - Handle video upload
- `GET /analysis/{video_id}` - Analysis page for specific video
- `POST /save_note` - Save analysis notes
- `GET /report/{video_id}` - Generate analysis report

## Database Schema

### Videos Table
- `id` (Primary Key)
- `filename` (Unique filename)
- `original_name` (User's filename)
- `file_size` (File size in bytes)
- `duration` (Video duration in seconds)
- `uploaded_at` (Upload timestamp)
- `status` (Processing status)

### Notes Table
- `id` (Primary Key)
- `video_id` (Foreign Key to Videos)
- `view_type` (video/audio/text)
- `prompt_id` (Foreign Key to Prompts)
- `content` (User's note content)
- `created_at` (Creation timestamp)

### Prompts Table
- `id` (Primary Key)
- `view_type` (video/audio/text)
- `question_text` (Prompt question)
- `order_index` (Display order)
- `active` (Enable/disable prompt)

## Deployment Options

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Railway will auto-detect Python and install dependencies
3. Set environment variables if needed
4. Deploy automatically

### Render
1. Connect repository to Render
2. Choose "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### DigitalOcean App Platform
1. Create new app from GitHub repository
2. Configure build and run commands
3. Deploy with automatic HTTPS

## Development Notes

- **Video Processing**: Uses MoviePy with graceful fallback if not available
- **Audio Processing**: Uses Librosa with graceful fallback for waveform visualization
- **File Storage**: Local filesystem (suitable for MVP, consider cloud storage for production)
- **Database**: SQLite (suitable for MVP, consider PostgreSQL for production)

## Future Enhancements

- [ ] Automatic speech-to-text transcription
- [ ] Advanced waveform visualization
- [ ] User authentication and accounts
- [ ] Cloud storage integration
- [ ] PDF report generation
- [ ] Video compression and optimization
- [ ] Analytics and progress tracking
- [ ] Mobile app version

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the GitHub repository.