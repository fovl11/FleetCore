from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import engine
router=APIRouter()
@router.get("",summary="Check API and database readiness")
def health():
 try:
  with engine.connect() as connection: connection.execute(text("SELECT 1"))
 except SQLAlchemyError:
  return JSONResponse(status_code=503,content={"status":"unavailable","service":"fleetcore-api","database":"unavailable"})
 return {"status":"ok","service":"fleetcore-api","database":"ok"}
