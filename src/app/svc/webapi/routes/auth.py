from fastapi import APIRouter

router = APIRouter(tags=["authentication"])


@router.post("verify-email")
def post_verify_email(email_address: str):
    pass
