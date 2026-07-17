from fastapi.testclient import TestClient
from app.main import app
def test_liveness():
 response=TestClient(app).get('/live');assert response.status_code==200;assert response.json()['status']=='ok';assert response.headers['x-request-id']
