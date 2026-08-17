from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.notification import NotificationType, NotificationPriority


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationOut]
    total: int
    unread_count: int


class AnnouncementCreate(BaseModel):
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    target_role: Optional[str] = None  # None = everyone