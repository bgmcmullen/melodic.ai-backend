from fastapi import APIRouter

healthcheck_router = APIRouter()

@healthcheck_router.get('/')
def test_server():
  return {"status": "ok", "message": "Server is running"}