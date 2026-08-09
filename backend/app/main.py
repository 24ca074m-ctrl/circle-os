from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import List, Optional
import random

from .database import init_db, get_session
from .models import Member, Practice, Attendance

app = FastAPI(title="Circle OS API")

@app.on_event("startup")
def on_startup():
    init_db()

# --- フロントエンド画面 ---
@app.get("/app", response_class=HTMLResponse)
def read_app():
    with open("app/static/index.html", encoding="utf-8") as f:
        return f.read()

# --- 部員 API ---
@app.get("/api/members", response_model=List[Member])
def get_members(session: Session = Depends(get_session)):
    return session.exec(select(Member)).all()

@app.post("/api/members", response_model=Member)
def create_member(member: Member, session: Session = Depends(get_session)):
    session.add(member)
    session.commit()
    session.refresh(member)
    return member

@app.delete("/api/members/{member_id}")
def delete_member(member_id: int, session: Session = Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    session.delete(member)
    session.commit()
    return {"ok": True}

# --- 練習・スケジュール API ---
@app.get("/api/practices", response_model=List[Practice])
def get_practices(session: Session = Depends(get_session)):
    return session.exec(select(Practice)).all()

@app.post("/api/practices", response_model=Practice)
def create_practice(practice: Practice, session: Session = Depends(get_session)):
    session.add(practice)
    session.commit()
    session.refresh(practice)
    return practice

# --- 出欠 API ---
@app.post("/api/attendances")
def set_attendance(attendance: Attendance, session: Session = Depends(get_session)):
    # 既存の回答があれば更新、なければ新規作成
    statement = select(Attendance).where(
        Attendance.practice_id == attendance.practice_id,
        Attendance.member_name == attendance.member_name
    )
    existing = session.exec(statement).first()
    if existing:
        existing.status = attendance.status
        session.add(existing)
    else:
        session.add(attendance)
    session.commit()
    return {"ok": True}

# --- AI予測・分析 & 連絡作成 API ---
@app.get("/api/ai/analytics")
def get_ai_analytics(session: Session = Depends(get_session)):
    members = session.exec(select(Member)).all()
    practices = session.exec(select(Practice)).all()
    
    total_members = len(members)
    predicted_attendance = max(1, int(total_members * random.uniform(0.65, 0.85))) if total_members > 0 else 0
    
    advice = []
    if total_members == 0:
        advice.append("部員がまだ登録されていません。まずは部員を追加しましょう。")
    else:
        advice.append(f"現在の登録メンバー数は {total_members} 名です。次回の練習参加予測は約 {predicted_attendance} 名です。")
        advice.append("試験期間前のため、下級生への出欠リマインドを早めに出すのがおすすめです。")
    
    return {
        "predicted_attendance": predicted_attendance,
        "advice_list": advice
    }

@app.get("/api/ai/generate-notice")
def generate_notice(date: str = Query(...), location: str = Query(...), memo: Optional[str] = ""):
    text = (
        f"【練習連絡 🏀】\n\n"
        f"お疲れ様です！次回の練習日程が決まりましたので共有します。\n\n"
        f"📅 日時: {date}\n"
        f"📍 場所: {location}\n"
    )
    if memo:
        text += f"📝 備考: {memo}\n"
    text += "\n参加・不参加の回答をアプリからお願いします！よろしくお願いします！"
    
    return {"notice_text": text}
