from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RUB Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API エンドポイント群
@app.get("/")
def root():
    return {"message": "Circle OS API is fully online!"}

@app.get("/dashboard")
def get_dashboard():
    return {
        "member_count": 40,
        "avg_attendance_rate": 78,
        "next_practice": {"date": "2026-08-12", "time": "18:00〜20:00", "venue": "立教大学体育館"},
        "prediction": {"predicted_count": 38, "confidence": 82}
    }

@app.get("/members")
def get_members():
    return [
        {"id": 1, "name": "山田", "grade": 3, "position": "G", "attendance_rate": 86, "payment": "支払済"},
        {"id": 2, "name": "佐藤", "grade": 2, "position": "F", "attendance_rate": 92, "payment": "支払済"},
        {"id": 3, "name": "鈴木", "grade": 4, "position": "C", "attendance_rate": 65, "payment": "未払い"},
        {"id": 4, "name": "田中", "grade": 1, "position": "G", "attendance_rate": 80, "payment": "未払い"},
    ]

@app.get("/practices")
def get_practices():
    return [
        {"id": 101, "date": "2026-08-12", "time": "18:00〜20:00", "venue": "立教大学体育館", "attended": 32, "absent": 5, "unanswered": 3},
        {"id": 102, "date": "2026-08-15", "time": "15:00〜17:00", "venue": "池袋体育館", "attended": 28, "absent": 8, "unanswered": 4},
    ]

@app.get("/venues")
def get_venues():
    return [
        {"id": 1, "name": "立教大学体育館", "price": 12000, "capacity": 80, "location": "池袋"},
        {"id": 2, "name": "池袋体育館", "price": 9000, "capacity": 60, "location": "池袋"},
        {"id": 3, "name": "豊島区スポーツセンター", "price": 15000, "capacity": 100, "location": "巣鴨"},
    ]

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

# スマホ向けフロントエンド画面 ( /app でアクセス )
@app.get("/app", response_class=HTMLResponse)
def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RUB Manager</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 text-gray-800 p-4 font-sans">
        <div class="max-w-md mx-auto space-y-4">
            <!-- ヘッダー -->
            <header class="bg-blue-600 text-white p-4 rounded-xl shadow-lg flex justify-between items-center">
                <h1 class="text-xl font-bold">RUB Manager</h1>
                <span class="text-xs bg-blue-500 px-2 py-1 rounded">Circle OS</span>
            </header>

            <!-- AIダッシュボードカード -->
            <section class="bg-white p-4 rounded-xl shadow border border-gray-100">
                <h2 class="text-sm font-semibold text-gray-500 mb-2">次回練習・AI予測</h2>
                <div class="text-lg font-bold text-blue-600 mb-1">8/12 18:00〜20:00</div>
                <div class="text-xs text-gray-600 mb-3">場所: 立教大学体育館</div>
                <div class="bg-blue-50 p-3 rounded-lg border border-blue-100 flex justify-between items-center">
                    <div>
                        <div class="text-xs text-gray-500">AI参加予測人数</div>
                        <div class="text-2xl font-extrabold text-blue-800">38 人</div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs text-gray-500">信頼度</div>
                        <div class="text-sm font-bold text-green-600">82%</div>
                    </div>
                </div>
            </section>

            <!-- スタッツ概要 -->
            <div class="grid grid-cols-2 gap-3">
                <div class="bg-white p-3 rounded-xl shadow text-center">
                    <div class="text-xs text-gray-500">総部員数</div>
                    <div class="text-xl font-bold">40 名</div>
                </div>
                <div class="bg-white p-3 rounded-xl shadow text-center">
                    <div class="text-xs text-gray-500">平均参加率</div>
                    <div class="text-xl font-bold text-green-600">78%</div>
                </div>
            </div>

            <!-- 部員一覧 -->
            <section class="bg-white p-4 rounded-xl shadow">
                <h2 class="text-sm font-semibold text-gray-500 mb-3">部員ステータス (一部)</h2>
                <div class="space-y-2" id="member-list">
                    <div class="flex justify-between items-center border-b pb-2">
                        <div>
                            <span class="font-bold">山田</span> <span class="text-xs text-gray-500">(3年/G)</span>
                        </div>
                        <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">参加率 86% / 支払済</span>
                    </div>
                    <div class="flex justify-between items-center border-b pb-2">
                        <div>
                            <span class="font-bold">鈴木</span> <span class="text-xs text-gray-500">(4年/C)</span>
                        </div>
                        <span class="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">参加率 65% / 未払い</span>
                    </div>
                </div>
            </section>

            <!-- AI分析インサイト -->
            <section class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-4 rounded-xl shadow">
                <h2 class="text-sm font-bold mb-2">💡 AI運営分析アドバイス</h2>
                <ul class="text-xs space-y-1 list-disc list-inside opacity-90">
                    <li>金曜日の参加率が低下傾向にあります</li>
                    <li>4年生の参加率フォローが必要です（現在 65%）</li>
                    <li>試験期間前は短時間練習を推奨します</li>
                </ul>
            </section>
        </div>
    </body>
    </html>
    """
