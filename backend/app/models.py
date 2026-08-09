from typing import Optional
from sqlmodel import Field, SQLModel

# 部員テーブル
class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    grade: int
    position: str
    attendance_rate: int = 100
    payment_status: str = "未払い"

# 練習予定テーブル
class Practice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    time: str
    venue: str
    attended_count: int = 0

# 体育館施設テーブル
class Venue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: int
    capacity: int
    location: str
