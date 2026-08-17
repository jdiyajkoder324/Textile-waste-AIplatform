from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.user import User
from app.models.waste import Waste
from app.models.textile_analysis import WasteClassification, ImageAnalysis
from app.models.sustainability_models import SustainabilityMetrics

# ---------------------------------------------------------------------------
# Thresholds — tune these as needed
# ---------------------------------------------------------------------------
UNPROCESSED_DAYS_THRESHOLD = 7
HIGH_INVENTORY_KG_THRESHOLD = 500
LOW_INVENTORY_KG_THRESHOLD = 20
HIGH_RECYCLABILITY_THRESHOLD = 85
SUSTAINABILITY_MILESTONE_THRESHOLD = 80
WASTE_DIVERSION_MILESTONE_THRESHOLD = 75


def create_notification(
    db: Session,
    type: NotificationType,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    user_id: Optional[int] = None,
    target_role: Optional[str] = None,
    created_by_id: Optional[int] = None,
) -> Notification:
    notif = Notification(
        type=type, title=title, message=message, priority=priority,
        user_id=user_id, target_role=target_role, created_by_id=created_by_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def _notification_exists_recently(db: Session, type: NotificationType, title: str, hours: int = 24) -> bool:
    """Avoid spamming duplicate alerts for the same condition."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return db.query(Notification).filter(
        Notification.type == type,
        Notification.title == title,
        Notification.created_at >= cutoff,
    ).first() is not None


def get_user_notifications(db: Session, user: User, unread_only: bool = False, limit: int = 50):
    query = db.query(Notification).filter(
        or_(
            Notification.user_id == user.id,
            Notification.target_role == user.role,
            and_(Notification.user_id.is_(None), Notification.target_role.is_(None)),  # platform-wide
        )
    )
    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    unread_count = query.filter(Notification.is_read == False).count() if not unread_only else total
    items = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return items, total, unread_count


def mark_read(db: Session, notification_id: int, user: User) -> bool:
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return False
    # only allow marking read if it was actually addressed to this user
    if notif.user_id is not None and notif.user_id != user.id and user.role != "Admin":
        return False
    notif.is_read = True
    db.commit()
    return True


def mark_all_read(db: Session, user: User) -> int:
    items, _, _ = get_user_notifications(db, user, unread_only=True, limit=1000)
    count = 0
    for n in items:
        n.is_read = True
        count += 1
    db.commit()
    return count


# ---------------------------------------------------------------------------
# Alert generation — scans real data, creates notifications when triggered.
# Call run_all_alert_checks(db) periodically (see routes for how to trigger).
# ---------------------------------------------------------------------------

def check_waste_collection_alerts(db: Session):
    cutoff = datetime.utcnow() - timedelta(days=UNPROCESSED_DAYS_THRESHOLD)
    stale_batches = db.query(Waste).filter(
        Waste.status == "Pending",
        Waste.created_at <= cutoff,
    ).all()

    for batch in stale_batches:
        title = f"Waste collection overdue — Batch {batch.batch_id or batch.id}"
        if _notification_exists_recently(db, NotificationType.WASTE_COLLECTION, title, hours=48):
            continue
        create_notification(
            db, NotificationType.WASTE_COLLECTION, title,
            f"Batch {batch.batch_id or batch.id} ({batch.quantity or 0} kg) has been pending for "
            f"more than {UNPROCESSED_DAYS_THRESHOLD} days. Consider scheduling collection.",
            priority=NotificationPriority.HIGH,
            user_id=batch.user_id,
        )


def check_recycling_opportunity_alerts(db: Session):
    high_value = db.query(WasteClassification).filter(
        WasteClassification.recyclability_percentage >= HIGH_RECYCLABILITY_THRESHOLD
    ).order_by(WasteClassification.created_at.desc()).limit(20).all()

    for wc in high_value:
        image = db.query(ImageAnalysis).filter(ImageAnalysis.id == wc.image_id).first()
        if not image:
            continue
        title = f"High-value recycling opportunity — {image.filename}"
        if _notification_exists_recently(db, NotificationType.RECYCLING_OPPORTUNITY, title, hours=24):
            continue
        create_notification(
            db, NotificationType.RECYCLING_OPPORTUNITY, title,
            f"{image.filename} shows {wc.recyclability_percentage:.0f}% recyclability "
            f"({wc.waste_category}). This is a strong recovery candidate.",
            priority=NotificationPriority.MEDIUM,
            user_id=image.user_id,
        )


def check_sustainability_milestone_alerts(db: Session):
    recent_metrics = db.query(SustainabilityMetrics).filter(
        SustainabilityMetrics.sustainability_index >= SUSTAINABILITY_MILESTONE_THRESHOLD
    ).order_by(SustainabilityMetrics.created_at.desc()).limit(10).all()

    for m in recent_metrics:
        title = f"Sustainability milestone reached — {m.material_type} batch"
        if _notification_exists_recently(db, NotificationType.SUSTAINABILITY_MILESTONE, title, hours=24):
            continue
        create_notification(
            db, NotificationType.SUSTAINABILITY_MILESTONE, title,
            f"A {m.material_type} batch achieved a sustainability index of "
            f"{m.sustainability_index:.0f}, rated '{m.sustainability_rating}'.",
            priority=NotificationPriority.MEDIUM,
            user_id=m.user_id,
        )

        if (m.diverted_percentage or 0) >= WASTE_DIVERSION_MILESTONE_THRESHOLD:
            div_title = f"Waste diversion target hit — {m.material_type} batch"
            if not _notification_exists_recently(db, NotificationType.SUSTAINABILITY_MILESTONE, div_title, hours=24):
                create_notification(
                    db, NotificationType.SUSTAINABILITY_MILESTONE, div_title,
                    f"{m.diverted_percentage:.0f}% of this {m.material_type} batch was diverted from landfill.",
                    priority=NotificationPriority.MEDIUM,
                    user_id=m.user_id,
                )


def check_inventory_warnings(db: Session):
    # group pending inventory by user
    users_with_batches = db.query(Waste.user_id).filter(Waste.user_id.isnot(None)).distinct().all()

    for (user_id,) in users_with_batches:
        pending_kg = db.query(Waste).filter(
            Waste.user_id == user_id, Waste.status == "Pending"
        ).all()
        total_pending = sum(b.quantity or 0 for b in pending_kg)

        if total_pending >= HIGH_INVENTORY_KG_THRESHOLD:
            title = f"High pending inventory — {total_pending:.0f} kg"
            if not _notification_exists_recently(db, NotificationType.INVENTORY_WARNING, title, hours=24):
                create_notification(
                    db, NotificationType.INVENTORY_WARNING, title,
                    f"You have {total_pending:.0f} kg of pending waste — consider prioritizing processing.",
                    priority=NotificationPriority.HIGH,
                    user_id=user_id,
                )
        elif 0 < total_pending <= LOW_INVENTORY_KG_THRESHOLD:
            title = f"Low inventory — {total_pending:.0f} kg remaining"
            if not _notification_exists_recently(db, NotificationType.INVENTORY_WARNING, title, hours=24):
                create_notification(
                    db, NotificationType.INVENTORY_WARNING, title,
                    f"Only {total_pending:.0f} kg of pending waste remains in your inventory.",
                    priority=NotificationPriority.LOW,
                    user_id=user_id,
                )


def run_all_alert_checks(db: Session):
    check_waste_collection_alerts(db)
    check_recycling_opportunity_alerts(db)
    check_sustainability_milestone_alerts(db)
    check_inventory_warnings(db)