from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from api_dashboard.database import get_session
from api_dashboard.models import SearchLog, User
from api_dashboard.security import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[SearchLog])
def get_history(session: Session = Depends(get_session),
current_user: User = Depends(get_current_user)):  # noqa: B008
    statement = select(SearchLog)
    # .order_by(SearchLog.created_at.desc())
    results = session.exec(statement).all()
    return results
