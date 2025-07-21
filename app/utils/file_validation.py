from fastapi import UploadFile
import os

def validate_video_file(file: UploadFile) -> dict:
    """
    Validate uploaded video file
    Returns dict with 'valid' boolean and 'error' message if invalid
    """
    
    # Check if file exists
    if not file:
        return {"valid": False, "error": "No file provided"}
    
    # Check file size (50MB limit)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    
    # Get file extension
    if not file.filename:
        return {"valid": False, "error": "Invalid filename"}
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Check if it's MP4
    allowed_extensions = ['.mp4']
    if file_extension not in allowed_extensions:
        return {"valid": False, "error": "Only MP4 files are supported"}
    
    # Check MIME type
    if file.content_type and not file.content_type.startswith('video/'):
        return {"valid": False, "error": "File must be a video"}
    
    # Note: We can't check file size here without reading the entire file
    # Size validation will be done after reading in the upload endpoint
    
    return {"valid": True, "error": None}

def check_file_size(content: bytes) -> dict:
    """
    Check if file content size is within limits
    """
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    
    if len(content) > MAX_FILE_SIZE:
        return {"valid": False, "error": f"File size exceeds 50MB limit. Current size: {len(content) / (1024*1024):.1f}MB"}
    
    return {"valid": True, "error": None}