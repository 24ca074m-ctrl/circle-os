import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- セキュリティ設定 ---
SECRET_KEY = os.getenv("SECRET_KEY", "circle-os-super-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1週間有効

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- DB接続設定 ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DB Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), default="部員")

class Practice(Base):
    __tablename__ = "practices"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    memo = Column(Text, nullable=True)

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    practice_id = Column(Integer, ForeignKey("practices.id"), nullable=False)
    member_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)

Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI(title="Circle OS API")

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

# --- 認証ユーティリティ ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証資格情報を検証できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: str = payload.get("sub")
        if student_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.student_id == student_id).first()
    if user is None:
        raise credentials_exception
    return user

# --- Pydantic Schemas ---
class UserRegister(BaseModel):
    student_id: str
    name: str
    password: str
    role: str = "部員"

class PracticeCreate(BaseModel):
    date: str
    location: str
    memo: str = ""

class AttendanceVote(BaseModel):
    practice_id: int
    status: str

# --- Endpoints ---
@app.get("/")
def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found"}

@app.post("/api/auth/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.student_id == user.student_id.upper()).first()
    if db_user:
        raise HTTPException(status_code=400, detail="この学籍番号は既に登録されています")
    hashed_pwd = get_password_hash(user.password)
    new_user = User(
        student_id=user.student_id.upper(),
        name=user.name,
        hashed_password=hashed_pwd,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "ユーザー登録が完了しました"}

@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == form_data.username.upper()).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="学籍番号またはパスワードが正しくありません")
    
    access_token = create_access_token(data={"sub": user.student_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
        "role": user.role
    }

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "student_id": current_user.student_id,
        "name": current_user.name,
        "role": current_user.role
    }

@app.get("/api/practices/")
def get_practices(db: Session = Depends(get_db)):
    return db.query(Practice).all()

@app.post("/api/practices/")
def create_practice(practice: PracticeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_p = Practice(date=practice.date, location=practice.location, memo=practice.memo)
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p

@app.post("/api/attendance/")
def vote_attendance(vote: AttendanceVote, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    att = db.query(Attendance).filter(
        Attendance.practice_id == vote.practice_id,
        Attendance.member_name == current_user.name
    ).first()
    if att:
        att.status = vote.status
    else:
        att = Attendance(practice_id=vote.practice_id, member_name=current_user.name, status=vote.status)
        db.add(att)
    db.commit()
    return {"message": "Success"}
