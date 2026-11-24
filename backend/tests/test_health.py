from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from app.main import app
from app.api.routes import health as health_route
class Connection:
 def __enter__(self): return self
 def __exit__(self,*args): return False
 def execute(self,statement): return 1
class Engine:
 def __init__(self,fail=False): self.fail=fail
 def connect(self):
  if self.fail: raise OperationalError("connect",{},Exception("down"))
  return Connection()
def test_health_ok(monkeypatch):
 monkeypatch.setattr(health_route,"engine",Engine()); response=TestClient(app).get("/api/v1/health"); assert response.status_code==200 and response.json()["database"]=="ok"
def test_health_unavailable(monkeypatch):
 monkeypatch.setattr(health_route,"engine",Engine(True)); response=TestClient(app).get("/api/v1/health"); assert response.status_code==503 and response.json()["database"]=="unavailable"
