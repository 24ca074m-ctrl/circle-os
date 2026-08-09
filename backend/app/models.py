from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    grade: str
    position: str
    role: str = Field(default="部員")  # 代表, 副代表, 会計, 部員 など

class Practice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    location: str
    memo: Optional[str] = None
    attendances: List["Attendance"] = Relationship(back_populates="practice")

class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    practice_id: int = Field(foreign_key="practice.id")
    member_name: str
    status: str  # 参加, 不参加, 未定
    practice: Optional[Practice] = Relationship(back_populates="attendances")
