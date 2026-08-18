from fastapi import APIRouter
from . import dev, auth


router = APIRouter()
router.include_router(dev.router, prefix="/_dev")
router.include_router(auth.router, prefix="/auth")
