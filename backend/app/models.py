from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_order=True, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    role = Column(String, default="部員")

class Practice(Base):
    __tablename__ = "practices"

    id = Column(Integer, primary_key=True, index=True)
    date_str = Column(String, nullable=False)  # 例: 2026-08-10 (18:00〜20:00)
    location = Column(String, nullable=False)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attendances = relationship("Attendance", back_populates="practice", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    practice_id = Column(Integer, ForeignKey("practices.id"), nullable=False)
    member_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # 参加 / 不参加 / 未定

    practice = relationship("Practice", back_populates="attendances")

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String, default="匿名部員")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
