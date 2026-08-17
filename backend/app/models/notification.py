import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base


class NotificationType(str, enum.Enum):
    WASTE_COLLECTION = "waste_collection"
    RECYCLING_OPPORTUNITY = "recycling_opportunity"
    SUSTAINABILITY_MILESTONE = "sustainability_milestone"
    INVENTORY_WARNING = "inventory_warning"
    ANNOUNCEMENT = "announcement"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # if user_id is set, it's targeted to one user. if role is set instead,
    # it's broadcast to everyone with that role. If both are null, it's platform-wide.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_role = Column(String(50), nullable=True, index=True)

    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM, nullable=False)

    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # set for admin announcements

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    created_by = relationship("User", foreign_keys=[created_by_id])