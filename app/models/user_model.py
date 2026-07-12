import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )