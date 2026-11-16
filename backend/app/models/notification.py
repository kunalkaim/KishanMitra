from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type = Column(String(50), default="system", nullable=False) # weather_alert, price_alert, advisory, system
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info", nullable=False) # info, warning, critical
    is_read = Column(Boolean, default=False, nullable=False)

    farmer = relationship("User", back_populates="notifications")
