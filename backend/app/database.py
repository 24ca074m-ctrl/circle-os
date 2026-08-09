import os
from sqlmodel import SQLModel, create_engine, Session

# 環境変数から DATABASE_URL を取得
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 先頭表記の揺れ（postgres:// や 大文字）を自動補正
if DATABASE_URL:
    if DATABASE_URL.lower().startswith("postgres://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[11:]
    elif DATABASE_URL.lower().startswith("postgresql://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[13:]

# URL内にデータベース名が誤って指定されている場合、安全なデフォルト('postgres')へ置換
if "circle_os_db" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("circle_os_db", "postgres")

# 接続エンジンの作成
engine = create_engine(DATABASE_URL if DATABASE_URL else "sqlite:///./test.db", echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
