from contextlib import contextmanager
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from app.main import app
from app import main

client = TestClient(app)

def test_live_and_demo_contract():
    assert client.get('/health/live').json() == {'status': 'ok', 'mode': 'demo'}
    data = client.get('/api/demo/courses').json()
    assert data['mode'] == 'demo' and data['persisted'] is False
    assert len(data['items']) == 3
    first = data['items'][0]
    assert client.get(f"/api/demo/courses/{first['id']}").json()['item'] == first

def test_missing_course_and_no_fake_writes():
    assert client.get('/api/demo/courses/missing').status_code == 404
    assert client.post('/api/demo/courses', json={'title': 'fake'}).status_code == 405
    assert client.post('/api/login', json={}).status_code == 404

def test_readiness_failure_does_not_leak_connection_secrets(monkeypatch):
    def broken():
        raise OperationalError('secret-query', {}, Exception('private-password'))
    monkeypatch.setattr(main.engine, 'connect', broken)
    response = client.get('/health/ready')
    assert response.status_code == 503
    assert 'private-password' not in response.text
    assert 'secret-query' not in response.text

def test_readiness_checks_database(monkeypatch):
    statements = []
    class Connection:
        def execute(self, statement):
            statements.append(str(statement))
    @contextmanager
    def connected():
        yield Connection()
    monkeypatch.setattr(main.engine, 'connect', connected)
    assert client.get('/health/ready').json()['schema'] == 'initial'
    assert statements == ['SELECT 1 FROM users LIMIT 1']

def test_cors_allows_only_configured_origin():
    allowed = client.options('/api/demo/courses', headers={'Origin': 'http://127.0.0.1:5173', 'Access-Control-Request-Method': 'GET'})
    denied = client.options('/api/demo/courses', headers={'Origin': 'https://untrusted.example', 'Access-Control-Request-Method': 'GET'})
    assert allowed.headers['access-control-allow-origin'] == 'http://127.0.0.1:5173'
    assert denied.status_code == 400
    assert 'access-control-allow-origin' not in denied.headers
