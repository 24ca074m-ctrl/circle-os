from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 1. 部員テーブル
class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)        # 氏名
    position = Column(String, default="")        # 学籍番号などを保存するカラム
    grade = Column(String, nullable=False)       # 学年 (例: 1年)
    role = Column(String, default="部員")        # 役職 (例: 代表, 一般部員)

# 2. 練習予定テーブル
class Practice(Base):
    __tablename__ = "practices"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)        # 開催日時 (例: 2026-08-10 (18:00〜20:00))
    location = Column(String, nullable=False)    # 場所 (例: 立教大学体育館)
    memo = Column(Text, default="")              # メモ・持ち物

    # 練習削除時に紐づく出欠データも自動削除する設定
    attendances = relationship("Attendance", back_populates="practice", cascade="all, delete-orphan")

# 3. 出欠投票テーブル
class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    practice_id = Column(Integer, ForeignKey("practices.id"), nullable=False) # どの練習か
    member_name = Column(String, nullable=False) # 誰が投票したか
    status = Column(String, nullable=False)      # 参加 / 不参加 / 未定

    practice = relationship("Practice", back_populates="attendances")

# 4. 意見箱テーブル
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String, default="匿名") # 送信者名
    content = Column(Text, nullable=False)       # ご意見・要望の本文
    created_at = Column(DateTime, default=datetime.utcnow) # 投稿日時
