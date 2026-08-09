from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade = Column(String, nullable=False)      # 例: 1年, 2年, 3年, 4年
    position = Column(String, nullable=False)   # 例: PG, SG, SF, PF, C
    role = Column(String, default="部員")        # 代表, 副代表, 会計, コート取り, 部員

class Practice(Base):
    __tablename__ = "practices"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    location = Column(String, nullable=False)
    memo = Column(Text, nullable=True)

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    practice_id = Column(Integer, ForeignKey("practices.id"), nullable=False)
    member_name = Column(String, nullable=False)
    status = Column(String, nullable=False)     # 参加, 不参加, 未定

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String, default="匿名")  # 匿名 または 部員名
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
