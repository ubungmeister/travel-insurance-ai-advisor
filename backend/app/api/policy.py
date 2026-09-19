from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.schemas.policy import PolicySummary
from app.services.policy_service import list_user_policies

router = APIRouter(prefix="/api/v1/policies", tags=["policy"])

@router.get("", response_model=list[PolicySummary])
def get_policies(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_user_policies(db, current_user.auth_user_id)