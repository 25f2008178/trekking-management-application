import enum
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase
from flask_security.models import sqla

from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Model(DeclarativeBase):
    pass

sqla.FsModels.set_db_info(base_model=Model)

# -- ENUMS --
class StaffStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_LEAVE = "On Leave"

class TrekDifficulty(str, enum.Enum):
    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"

class TrekStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    OPEN = "Open"
    CLOSED = "Closed"
    COMPLETED = "Completed"

class BookingStatus(str, enum.Enum):
    BOOKED = "Booked"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


# -- MODELS --
class Role(Model, sqla.FsRoleMixin):
    __tablename__ = "role"

class User(Model, sqla.FsUserMixin):
    __tablename__ = "user"
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    staff_profile: Mapped[Optional["StaffProfile"]] = relationship(
        "StaffProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )

class StaffProfile(Model):
    __tablename__ = "staff_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    status: Mapped[StaffStatus] = mapped_column(
        Enum(StaffStatus), 
        default=StaffStatus.ACTIVE, 
        nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="staff_profile")
    assigned_treks: Mapped[List["Trek"]] = relationship("Trek", back_populates="assigned_staff")

class Trek(Model):
    __tablename__ = "trek"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trek_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[TrekDifficulty] = mapped_column(
        Enum(TrekDifficulty), 
        nullable=False
    )
    
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # in days
    available_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[TrekStatus] = mapped_column(
        Enum(TrekStatus), 
        default=TrekStatus.PENDING, 
        nullable=False
    )

    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    assigned_staff_id: Mapped[Optional[int]] = mapped_column(ForeignKey("staff_profile.id"), nullable=True)

    assigned_staff: Mapped[Optional["StaffProfile"]] = relationship("StaffProfile", back_populates="assigned_treks")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="trek", cascade="all, delete-orphan")


class Booking(Model):
    __tablename__ = "booking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    trek_id: Mapped[int] = mapped_column(ForeignKey("trek.id"), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=(lambda: datetime.now(timezone.utc)), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), 
        default=BookingStatus.BOOKED, 
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    trek: Mapped["Trek"] = relationship("Trek", back_populates="bookings")