import pytest
from fastapi.testclient import TestClient
from app.models import Video
from app.database import get_db

@pytest.fixture
def test_video(client, test_user):
    """Fixture to create a test video"""
    db = next(get_db())
    video = Video(filename="test_video.mp4", user_id=test_user.id)
    db.add(video)
    db.commit()
    return video

def test_video_playback(client, test_user, test_video):
    """Test successful video playback"""
    # Login and get video
    client.post('/login', data={
        'email': test_user.email,
        'password': 'testpassword'
    })
    response = client.get(f'/video/{test_video.id}')
    
    assert response.status_code == 200
    assert response.headers['content-type'] == 'video/mp4'
    assert int(response.headers['content-length']) > 0

def test_video_seeking(client, test_user, test_video):
    """Test byte-range requests for seeking"""
    headers = {'Range': 'bytes=0-999'} 
    response = client.get(f'/video/{test_video.id}', headers=headers)
    
    assert response.status_code == 206  # Partial Content
    assert 'content-range' in response.headers
    assert response.headers['accept-ranges'] == 'bytes'

def test_unauthorized_playback(client, test_video):
    """Test access control for videos"""
    # Not logged in
    response = client.get(f'/video/{test_video.id}')
    assert response.status_code == 403
    
    # Wrong user
    other_user = test_user  # Reuse fixture
    client.post('/login', data={
        'email': other_user.email,
        'password': 'testpassword'
    })
    response = client.get(f'/video/{test_video.id}')
    assert response.status_code == 403

def test_video_metadata(client, test_user, test_video):
    """Test video metadata endpoint"""
    client.post('/login', data={
        'email': test_user.email,
        'password': 'testpassword'
    })
    response = client.get(f'/video/{test_video.id}/info')
    assert response.status_code == 200
    data = response.json()
    assert 'duration' in data
    assert data['duration'] > 0
    assert 'resolution' in data
    assert 'file_size' in data