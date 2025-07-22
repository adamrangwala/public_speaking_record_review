import pytest
import os
from fastapi.testclient import TestClient
from app.models import Video

def test_video_upload(client, test_user):
    # Login first
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })

    # Upload test video
    test_video_path = os.path.join(os.path.dirname(__file__), 'test_video.mp4')
    with open(test_video_path, 'rb') as video_file:
        response = client.post('/upload', files={'file': video_file})
    
    assert response.status_code == 200
    assert b"Upload successful" in response.data

    # Verify video exists in database
    db = next(client.app.dependency_overrides[get_db]())
    video = db.query(Video).filter(Video.user_id == test_user.id).first()
    assert video is not None

def test_video_access(client, test_user):
    # Test unauthorized access
    response = client.get('/video/1')
    assert response.status_code == 403

    # Login and test authorized access
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    response = client.get('/video/1')
    assert response.status_code == 200