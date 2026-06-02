from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas import CurrentUserResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.code if current_user.role else None,
        is_active=current_user.is_active,
    )
