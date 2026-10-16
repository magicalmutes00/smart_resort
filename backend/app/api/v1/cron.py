"""Cron trigger routes.

Render's cron jobs have no free tier, so on the free plan the 15-minute
schedule is driven from the outside (GitHub Actions) by POSTing here with the
shared ``CRON_TOKEN``. The endpoint runs the same job the Render Cron service
would run (``python -m app.jobs.auto_assign``).
"""
import hmac
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.config import settings

router = APIRouter()


def require_cron_token(
    x_cron_token: Optional[str] = Header(default=None, alias="X-Cron-Token"),
) -> None:
    """Fail closed: the trigger is unusable unless CRON_TOKEN is set and matches."""
    expected = settings.CRON_TOKEN
    if not expected:
        raise HTTPException(status_code=503, detail="Cron trigger is not configured")
    if not x_cron_token or not hmac.compare_digest(x_cron_token, expected):
        raise HTTPException(status_code=401, detail="Invalid cron token")


@router.post("/run", dependencies=[Depends(require_cron_token)])
def run_scheduled_jobs() -> dict:
    """Run the scheduled work: assignment, escalation, stale food-order check."""
    from app.jobs.auto_assign import run

    return run()
