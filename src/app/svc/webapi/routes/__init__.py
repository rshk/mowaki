from fastapi import APIRouter

from . import auth, dev

router = APIRouter()
router.include_router(dev.router, prefix="/_dev")
router.include_router(auth.router, prefix="/auth")
