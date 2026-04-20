from fastapi import APIRouter

from app.api.v1.routes import auth
from app.api.v1.routes import leads

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(leads.router, prefix="", tags=["leads"])
