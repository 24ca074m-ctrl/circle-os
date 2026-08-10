import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- DB接続設定 ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DB Models ---
class MemberDB(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    grade = Column(String(20), nullable=False)
    role = Column(String(50), nullable=False)

class PracticeDB(Base):
    __tablename__ = "practices"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    memo = Column(Text, nullable=True)

class AttendanceDB(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    practice_id = Column(Integer, nullable=False)
    member_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)

class FeedbackDB(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String(100), default="匿名部員")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI(title="RUB Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初期代表者の自動登録チェック
def init_admin():
    db = SessionLocal()
    try:
        admin = db.query(MemberDB).filter(MemberDB.student_id == "24CA074M").first()
        if not admin:
            new_admin = MemberDB(
                student_id="24CA074M",
                name="代表者",
                grade="3年",
                role="代表"
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()

init_admin()

# --- Schemas ---
class MemberCreate(BaseModel):
    student_id: str
    name: str
    grade: str
    role: str

class PracticeCreate(BaseModel):
    date: str
    location: str
    memo: str = ""

class AttendanceVote(BaseModel):
    practice_id: int
    member_name: str
    status: str

class FeedbackCreate(BaseModel):
    sender_name: Optional[str] = "匿名部員"
    content: str

# --- Routes ---
@app.get("/")
def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found"}

# 部員 API
@app.get("/api/members/")
def get_members(db: Session = Depends(get_db)):
    return db.query(MemberDB).all()

@app.post("/api/members/")
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    db_m = db.query(MemberDB).filter(MemberDB.student_id == member.student_id.upper()).first()
    if db_m:
        raise HTTPException(status_code=400, detail="学籍番号が既に登録されています")
    new_m = MemberDB(
        student_id=member.student_id.upper(),
        name=member.name,
        grade=member.grade,
        role=member.role
    )
    db.add(new_m)
    db.commit()
    db.refresh(new_m)
    return new_m

@app.delete("/api/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    m = db.query(MemberDB).filter(MemberDB.id == member_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="部員が見つかりません")
    db.delete(m)
    db.commit()
    return {"message": "Deleted"}

# 練習 API
@app.get("/api/practices/")
def get_practices(db: Session = Depends(get_db)):
    return db.query(PracticeDB).all()

@app.post("/api/practices/")
def create_practice(practice: PracticeCreate, db: Session = Depends(get_db)):
    new_p = PracticeDB(date=practice.date, location=practice.location, memo=practice.memo)
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p

@app.delete("/api/practices/{practice_id}")
def delete_practice(practice_id: int, db: Session = Depends(get_db)):
    p = db.query(PracticeDB).filter(PracticeDB.id == practice_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="練習が見つかりません")
    db.delete(p)
    db.commit()
    return {"message": "Deleted"}

# 出欠 API
@app.get("/api/attendance/")
def get_attendance(db: Session = Depends(get_db)):
    return db.query(AttendanceDB).all()

@app.post("/api/attendance/")
def vote_attendance(vote: AttendanceVote, db: Session = Depends(get_db)):
    att = db.query(AttendanceDB).filter(
        AttendanceDB.practice_id == vote.practice_id,
        AttendanceDB.member_name == vote.member_name
    ).first()
    if att:
        att.status = vote.status
    else:
        att = AttendanceDB(practice_id=vote.practice_id, member_name=vote.member_name, status=vote.status)
        db.add(att)
    db.commit()
    return {"message": "Success"}

# 意見箱 API
@app.get("/api/feedbacks/")
def get_feedbacks(db: Session = Depends(get_db)):
    return db.query(FeedbackDB).order_by(FeedbackDB.created_at.desc()).all()

@app.post("/api/feedbacks/")
def create_feedback(fb: FeedbackCreate, db: Session = Depends(get_db)):
    sender = fb.sender_name if fb.sender_name else "匿名部員"
    new_fb = FeedbackDB(sender_name=sender, content=fb.content)
    db.add(new_fb)
    db.commit()
    db.refresh(new_fb)
    return new_fb

@app.delete("/api/feedbacks/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    f = db.query(FeedbackDB).filter(FeedbackDB.id == feedback_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="意見が見つかりません")
    db.delete(f)
    db.commit()
    return {"message": "Deleted"}
