import pytest
from app.database import get_db
from app.models import User

def test_user_registration(client):
    # Test successful registration
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'securepassword123',
        'confirm_password': 'securepassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data
    
    # Verify user exists in database
    db = get_db()
    user = db.query(User).filter(User.email == 'test@example.com').first()
    assert user is not None

def test_user_login(client, test_user):
    # Test successful login
    response = client.post('/login', data={
        'email': test_user.email,
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_protected_route_access(client, test_user):
    # Test unauthorized access
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login
    
    # Test authorized access
    client.post('/login', data={
        'email': test_user.email,
        'password': 'testpassword'
    })
    response = client.get('/profile')
    assert response.status_code == 200