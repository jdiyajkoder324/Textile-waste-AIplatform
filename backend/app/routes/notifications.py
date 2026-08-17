from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.notification import NotificationOut, NotificationListResponse, AnnouncementCreate
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, unread_count = notification_service.get_user_notifications(db, current_user, unread_only, limit)
    return NotificationListResponse(items=items, total=total, unread_count=unread_count)


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = notification_service.mark_read(db, notification_id, current_user)
    if not ok:
        raise HTTPException(404, "Notification not found")
    return {"message": "Marked as read"}


@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = notification_service.mark_all_read(db, current_user)
    return {"message": f"Marked {count} notification(s) as read"}


@router.post("/announcements", response_model=NotificationOut)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
):
    from app.models.notification import NotificationType
    notif = notification_service.create_notification(
        db, NotificationType.ANNOUNCEMENT, payload.title, payload.message,
        priority=payload.priority, target_role=payload.target_role, created_by_id=current_user.id,
    )
    return notif


@router.post("/check-alerts")
def trigger_alert_checks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
):
    """Manually trigger a scan of platform data for alert conditions.
    In production this would run on a schedule (cron/Celery beat) instead."""
    notification_service.run_all_alert_checks(db)
    return {"message": "Alert checks completed"}