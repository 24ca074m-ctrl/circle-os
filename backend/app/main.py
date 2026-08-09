from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RUB Manager - Circle OS")

# Pydantic Schemas
class MemberCreate(BaseModel):
    name: str
    grade: str
    role: str = "部員"

class MemberResponse(MemberCreate):
    id: int
    class Config:
        from_attributes = True

class PracticeCreate(BaseModel):
    date: str
    location: str
    memo: Optional[str] = None

class PracticeResponse(PracticeCreate):
    id: int
    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    practice_id: int
    member_name: str
    status: str

class FeedbackCreate(BaseModel):
    sender_name: Optional[str] = "匿名"
    content: str

# API Routes
@app.get("/api/members", response_model=List[MemberResponse])
def get_members(db: Session = Depends(get_db)):
    return db.query(models.Member).all()

@app.post("/api/members", response_model=MemberResponse)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    db_member = models.Member(
        name=member.name,
        grade=member.grade,
        position="", # ポジション廃止に伴い空文字設定
        role=member.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.delete("/api/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    m = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(m)
    db.commit()
    return {"message": "Member deleted"}

@app.get("/api/practices", response_model=List[PracticeResponse])
def get_practices(db: Session = Depends(get_db)):
    return db.query(models.Practice).all()

@app.post("/api/practices", response_model=PracticeResponse)
def create_practice(practice: PracticeCreate, db: Session = Depends(get_db)):
    db_practice = models.Practice(**practice.dict())
    db.add(db_practice)
    db.commit()
    db.refresh(db_practice)
    return db_practice

@app.delete("/api/practices/{practice_id}")
def delete_practice(practice_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Practice).filter(models.Practice.id == practice_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Practice not found")
    db.delete(p)
    db.commit()
    return {"message": "Practice deleted"}

# 出欠API
@app.post("/api/attendance")
def vote_attendance(att: AttendanceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Attendance).filter(
        models.Attendance.practice_id == att.practice_id,
        models.Attendance.member_name == att.member_name
    ).first()
    
    if existing:
        existing.status = att.status
    else:
        new_att = models.Attendance(**att.dict())
        db.add(new_att)
    
    db.commit()
    return {"message": "Attendance recorded"}

@app.get("/api/attendance/{practice_id}")
def get_attendance(practice_id: int, db: Session = Depends(get_db)):
    atts = db.query(models.Attendance).filter(models.Attendance.practice_id == practice_id).all()
    summary = {"参加": [], "不参加": [], "未定": []}
    for a in atts:
        if a.status in summary:
            summary[a.status].append(a.member_name)
    return summary

# 意見箱API
@app.post("/api/feedbacks")
def create_feedback(fb: FeedbackCreate, db: Session = Depends(get_db)):
    new_fb = models.Feedback(**fb.dict())
    db.add(new_fb)
    db.commit()
    return {"message": "Feedback submitted"}

@app.get("/api/feedbacks")
def get_feedbacks(db: Session = Depends(get_db)):
    fbs = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()
    return fbs

# AI アナリティクス
@app.get("/api/ai/analytics")
def get_ai_analytics(db: Session = Depends(get_db)):
    member_count = db.query(models.Member).count()
    predicted = int(member_count * 0.7) if member_count > 0 else 0
    advices = [
        f"現在の登録部員数は {member_count} 名です。",
        f"次回の予想参加人数は約 {predicted} 名です。",
        "コート予約枠が不足しないよう、早めにコート取り担当へ共有してください。"
    ]
    return {
        "member_count": member_count,
        "predicted_attendance": predicted,
        "advice_list": advices
    }

# 静的ファイル配信
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/app")
def read_app():
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "index.html not found"}

@app.get("/")
def read_root():
    return {"message": "Circle OS Backend with FastApi & SQLite"}
