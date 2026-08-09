from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RUB Manager API")

# CORS設定（フロントエンドからの接続許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# トップ画面
@app.get("/")
def root():
    return {"message": "Circle OS API is fully online!"}

# 1. ダッシュボード API
@app.get("/dashboard")
def get_dashboard():
    return {
        "member_count": 40,
        "avg_attendance_rate": 78,
        "next_practice": {
            "date": "2026-08-12",
            "time": "18:00〜20:00",
            "venue": "立教大学体育館"
        },
        "prediction": {
            "predicted_count": 38,
            "confidence": 82
        }
    }

# 2. 部員管理 API
@app.get("/members")
def get_members():
    return [
        {"id": 1, "name": "山田", "grade": 3, "position": "G", "attendance_rate": 86, "payment": "支払済"},
        {"id": 2, "name": "佐藤", "grade": 2, "position": "F", "attendance_rate": 92, "payment": "支払済"},
        {"id": 3, "name": "鈴木", "grade": 4, "position": "C", "attendance_rate": 65, "payment": "未払い"},
        {"id": 4, "name": "田中", "grade": 1, "position": "G", "attendance_rate": 80, "payment": "未払い"},
    ]

# 3. 練習・出欠管理 API
@app.get("/practices")
def get_practices():
    return [
        {"id": 101, "date": "2026-08-12", "time": "18:00〜20:00", "venue": "立教大学体育館", "attended": 32, "absent": 5, "unanswered": 3},
        {"id": 102, "date": "2026-08-15", "time": "15:00〜17:00", "venue": "池袋体育館", "attended": 28, "absent": 8, "unanswered": 4},
    ]

# 4. 体育館管理 API
@app.get("/venues")
def get_venues():
    return [
        {"id": 1, "name": "立教大学体育館", "price": 12000, "capacity": 80, "location": "池袋"},
        {"id": 2, "name": "池袋体育館", "price": 9000, "capacity": 60, "location": "池袋"},
        {"id": 3, "name": "豊島区スポーツセンター", "price": 15000, "capacity": 100, "location": "巣鴨"},
    ]

# 5. 会費管理 API
@app.get("/payments")
def get_payments():
    return {
        "collection_rate": 75,
        "paid_count": 30,
        "unpaid_count": 10,
        "unpaid_members": ["鈴木", "田中"]
    }

# 6. AI 参加人数予測 & 運営分析 API
@app.get("/ai/analyze")
def get_ai_analysis():
    return {
        "predicted_attendance": 38,
        "confidence": 82,
        "insights": [
            "金曜日の参加率が低い傾向があります",
            "4年生の参加率が低下しています（65%）",
            "試験期間前の練習調整を推奨します"
        ]
    }
