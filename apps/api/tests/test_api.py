import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import os

# Override database URL to use SQLite for tests
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get('/api/v1/health')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_register_user(client):
    import uuid
    unique_email = f'user_{uuid.uuid4()}@example.com'
    resp = await client.post('/api/v1/auth/register', json={
        'email': unique_email,
        'password': 'password123',
        'name': 'Test User',
    })
    assert resp.status_code == 200
    data = resp.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post('/api/v1/auth/register', json={
        'email': 'dup@example.com', 'password': 'password123',
    })
    resp = await client.post('/api/v1/auth/register', json={
        'email': 'dup@example.com', 'password': 'password123',
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post('/api/v1/auth/register', json={
        'email': 'login@example.com', 'password': 'password123',
    })
    resp = await client.post('/api/v1/auth/login', json={
        'email': 'login@example.com', 'password': 'password123',
    })
    assert resp.status_code == 200
    assert 'access_token' in resp.json()


@pytest.mark.asyncio
async def test_login_invalid(client):
    resp = await client.post('/api/v1/auth/login', json={
        'email': 'noone@example.com', 'password': 'wrong',
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'refresh@example.com', 'password': 'password123',
    })
    refresh_token = reg.json()['refresh_token']

    resp = await client.post('/api/v1/auth/refresh', json={
        'refresh_token': refresh_token,
    })
    assert resp.status_code == 200
    assert 'access_token' in resp.json()


@pytest.mark.asyncio
async def test_me_authenticated(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'me@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']

    resp = await client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.json()['email'] == 'me@example.com'


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get('/api/v1/auth/me')
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_project(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'proj@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']

    resp = await client.post('/api/v1/projects', json={
        'name': 'My Test Project',
    }, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    data = resp.json()
    assert data['name'] == 'My Test Project'
    assert 'id' in data


@pytest.mark.asyncio
async def test_list_projects(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'list@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']

    await client.post('/api/v1/projects', json={'name': 'P1'},
                      headers={'Authorization': f'Bearer {token}'})
    await client.post('/api/v1/projects', json={'name': 'P2'},
                      headers={'Authorization': f'Bearer {token}'})

    resp = await client.get('/api/v1/projects',
                            headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.json()['total'] >= 2


@pytest.mark.asyncio
async def test_update_project(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'update@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']
    proj = await client.post('/api/v1/projects', json={'name': 'Old'},
                             headers={'Authorization': f'Bearer {token}'})
    pid = proj.json()['id']

    resp = await client.put(f'/api/v1/projects/{pid}', json={'name': 'New'},
                            headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.json()['name'] == 'New'


@pytest.mark.asyncio
async def test_delete_project(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'delete@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']
    proj = await client.post('/api/v1/projects', json={'name': 'Del'},
                             headers={'Authorization': f'Bearer {token}'})
    pid = proj.json()['id']

    resp = await client.delete(f'/api/v1/projects/{pid}',
                               headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_create_preset(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'preset@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']

    resp = await client.post('/api/v1/presets', json={
        'name': 'My Warm Design',
        'room_type': 'bedroom',
        'style': 'warm',
        'preset_data': {'wallColor': '#e8d5c4', 'floorColor': '#a0845c'},
    }, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    assert resp.json()['name'] == 'My Warm Design'


@pytest.mark.asyncio
async def test_list_presets(client):
    reg = await client.post('/api/v1/auth/register', json={
        'email': 'presetlist@example.com', 'password': 'password123',
    })
    token = reg.json()['access_token']

    resp = await client.get('/api/v1/presets',
                            headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'presets' in resp.json()
