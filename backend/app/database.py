import os
from sqlmodel import SQLModel, create_engine, Session

# 環境変数から DATABASE_URL を取得
DATABASE_URL = os.getenv("DATABASE_URL")

# RenderのPostgreSQL URL (postgres://) を SQLAlchemy標準 (postgresql://) に自動変換
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# データベースエンジンの作成
engine = create_engine(DATABASE_URL if DATABASE_URL else "sqlite:///./test.db", echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
