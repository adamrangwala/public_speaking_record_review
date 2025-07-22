import pytest
import os
from fastapi.testclient import TestClient
from app.utils.file_validation import validate_video_file

def test_video_file_validation(client):
    """Test valid video file upload"""
    # Create a small valid video file for testing
    test_video = os.path.join(os.path.dirname(__file__), 'test_video.mp4')
    with open(test_video, 'rb') as video_file:
        response = client.post('/upload', files={'file': video_file})
        assert response.status_code == 200
        assert b"Upload successful" in response.data

def test_invalid_file_type(client):
    """Test invalid file type rejection"""
    # Create a text file to simulate invalid upload
    invalid_file = os.path.join(os.path.dirname(__file__), 'invalid.txt')
    with open(invalid_file, 'w') as f:
        f.write("Not a video file")
    
    with open(invalid_file, 'rb') as f:
        response = client.post('/upload', files={'file': f})
        assert response.status_code == 400
        assert b"Invalid file type" in response.data

def test_file_size_validation(client):
    """Test file size limit enforcement"""
    # Create a file that exceeds size limit (assuming 100MB limit)
    large_file = os.path.join(os.path.dirname(__file__), 'large_file.mp4')
    with open(large_file, 'wb') as f:
        f.seek(100 * 1024 * 1024)  # 100MB
        f.write(b'0')
    
    with open(large_file, 'rb') as f:
        response = client.post('/upload', files={'file': f})
        assert response.status_code == 413
        assert b"File too large" in response.data

@pytest.mark.asyncio
async def test_validate_video_file_function():
    """Test the validation function directly"""
    test_video = os.path.join(os.path.dirname(__file__), 'test_video.mp4')
    with open(test_video, 'rb') as f:
        result = await validate_video_file(f)
        assert result["valid"] is True

    invalid_file = os.path.join(os.path.dirname(__file__), 'invalid.txt')
    with open(invalid_file, 'w') as f:
        f.write("Not a video")
    with open(invalid_file, 'rb') as f:
        result = await validate_video_file(f)
        assert result["valid"] is False