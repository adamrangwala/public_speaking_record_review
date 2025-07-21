import os
import numpy as np

try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("Warning: moviepy not available. Video processing will be limited.")

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available. Audio processing will be limited.")

def process_video(file_path: str) -> float:
    """
    Process video file and extract basic information
    Returns video duration in seconds
    """
    if not MOVIEPY_AVAILABLE:
        print("MoviePy not available, using file-based approach")
        # For now, return None to indicate duration should be detected by browser
        return None
    
    try:
        # Load video file
        video = VideoFileClip(file_path)
        duration = video.duration
        
        # Extract audio for future processing (skip for now if failing)
        try:
            audio_path = file_path.replace('.mp4', '_audio.wav')
            if video.audio:
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        except Exception as audio_error:
            print(f"Audio extraction failed: {audio_error}")
        
        # Close video file to free memory
        video.close()
        
        return duration
        
    except Exception as e:
        print(f"Error processing video: {e}")
        return None  # Return None to let browser detect duration

def extract_audio_features(file_path: str) -> dict:
    """
    Extract audio features for waveform visualization
    Returns dictionary with audio data
    """
    if not LIBROSA_AVAILABLE or not MOVIEPY_AVAILABLE:
        print("Audio processing libraries not available, returning empty data")
        return {
            "waveform": [],
            "time": [],
            "sample_rate": 22050,
            "duration": 0
        }
    
    try:
        # Get audio file path
        audio_path = file_path.replace('.mp4', '_audio.wav')
        
        if not os.path.exists(audio_path):
            # Extract audio if it doesn't exist
            video = VideoFileClip(file_path)
            if video.audio:
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
        
        if not os.path.exists(audio_path):
            return {
                "waveform": [],
                "time": [],
                "sample_rate": 22050,
                "duration": 0
            }
        
        # Load audio with librosa
        y, sr = librosa.load(audio_path)
        
        # Generate time axis
        duration = len(y) / sr
        time = np.linspace(0, duration, len(y))
        
        # Downsample for visualization (take every nth sample)
        downsample_factor = max(1, len(y) // 1000)  # Limit to ~1000 points
        y_downsampled = y[::downsample_factor]
        time_downsampled = time[::downsample_factor]
        
        return {
            "waveform": y_downsampled.tolist(),
            "time": time_downsampled.tolist(),
            "sample_rate": sr,
            "duration": duration
        }
        
    except Exception as e:
        print(f"Error extracting audio features: {e}")
        return {
            "waveform": [],
            "time": [],
            "sample_rate": 22050,
            "duration": 0
        }

def get_video_info(file_path: str) -> dict:
    """
    Get basic video information
    """
    if not MOVIEPY_AVAILABLE:
        return {
            "duration": 60.0,
            "fps": 30,
            "size": [1920, 1080],
            "has_audio": True
        }
    
    try:
        video = VideoFileClip(file_path)
        info = {
            "duration": video.duration,
            "fps": video.fps,
            "size": video.size,
            "has_audio": video.audio is not None
        }
        video.close()
        return info
        
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {
            "duration": 60.0,
            "fps": 30,
            "size": [1920, 1080],
            "has_audio": True
        }