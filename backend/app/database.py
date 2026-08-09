import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "")

# 先頭のプロトコル表記補正とDB名の置換
if DATABASE_URL:
    if DATABASE_URL.startswith("Postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("Postgresql://", "postgresql://")
    elif DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    
    if "circle_os_db" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("circle_os_db", "postgres")

engine = create_engine(DATABASE_URL if DATABASE_URL else "sqlite:///./test.db", echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
