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

@app.get("/")
def root():
    return {"message": "Circle OS API is fully online!"}

# UI画面 ( /app )
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
    <body class="bg-gray-100 text-gray-800 pb-20 font-sans">
        <div class="max-w-md mx-auto p-4 space-y-4">
            
            <!-- ヘッダー -->
            <header class="bg-blue-600 text-white p-4 rounded-xl shadow-lg flex justify-between items-center">
                <h1 class="text-xl font-bold">RUB Manager</h1>
                <span class="text-xs bg-blue-500 px-2 py-1 rounded">Circle OS</span>
            </header>

            <!-- タブ 1: ダッシュボード -->
            <div id="tab-dashboard" class="tab-content space-y-4">
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

                <section class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-4 rounded-xl shadow">
                    <h2 class="text-sm font-bold mb-2">💡 AI運営分析</h2>
                    <ul class="text-xs space-y-1 list-disc list-inside opacity-90">
                        <li>金曜日の参加率が低下傾向にあります</li>
                        <li>4年生の参加率フォローが必要です（65%）</li>
                    </ul>
                </section>
            </div>

            <!-- タブ 2: 部員管理 -->
            <div id="tab-members" class="tab-content hidden space-y-3">
                <h2 class="text-md font-bold text-gray-700">部員一覧 (40名)</h2>
                <div class="bg-white p-4 rounded-xl shadow space-y-3">
                    <div class="flex justify-between items-center border-b pb-2">
                        <div>
                            <div class="font-bold">山田 太郎</div>
                            <div class="text-xs text-gray-500">3年 / ガード (G)</div>
                        </div>
                        <span class="text-xs bg-green-100 text-green-700 font-bold px-2.5 py-1 rounded-full">参加 86% / 済</span>
                    </div>
                    <div class="flex justify-between items-center border-b pb-2">
                        <div>
                            <div class="font-bold">佐藤 花子</div>
                            <div class="text-xs text-gray-500">2年 / フォワード (F)</div>
                        </div>
                        <span class="text-xs bg-green-100 text-green-700 font-bold px-2.5 py-1 rounded-full">参加 92% / 済</span>
                    </div>
                    <div class="flex justify-between items-center border-b pb-2">
                        <div>
                            <div class="font-bold">鈴木 健太</div>
                            <div class="text-xs text-gray-500">4年 / センター (C)</div>
                        </div>
                        <span class="text-xs bg-red-100 text-red-700 font-bold px-2.5 py-1 rounded-full">参加 65% / 未払い</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <div>
                            <div class="font-bold">田中 翔</div>
                            <div class="text-xs text-gray-500">1年 / ガード (G)</div>
                        </div>
                        <span class="text-xs bg-red-100 text-red-700 font-bold px-2.5 py-1 rounded-full">参加 80% / 未払い</span>
                    </div>
                </div>
            </div>

            <!-- タブ 3: 体育館管理 -->
            <div id="tab-venues" class="tab-content hidden space-y-3">
                <h2 class="text-md font-bold text-gray-700">体育館施設一覧</h2>
                <div class="space-y-2">
                    <div class="bg-white p-3 rounded-xl shadow border-l-4 border-blue-500">
                        <div class="font-bold">立教大学体育館</div>
                        <div class="text-xs text-gray-500">料金: 12,000円 | 定員: 80人 | 池袋</div>
                    </div>
                    <div class="bg-white p-3 rounded-xl shadow border-l-4 border-green-500">
                        <div class="font-bold">池袋体育館</div>
                        <div class="text-xs text-gray-500">料金: 9,000円 | 定員: 60人 | 池袋</div>
                    </div>
                    <div class="bg-white p-3 rounded-xl shadow border-l-4 border-yellow-500">
                        <div class="font-bold">豊島区スポーツセンター</div>
                        <div class="text-xs text-gray-500">料金: 15,000円 | 定員: 100人 | 巣鴨</div>
                    </div>
                </div>
            </div>

            <!-- タブ 4: AI連絡文生成 -->
            <div id="tab-ai" class="tab-content hidden space-y-3">
                <h2 class="text-md font-bold text-gray-700">🤖 AI連絡文作成</h2>
                <div class="bg-white p-4 rounded-xl shadow space-y-3">
                    <label class="block text-xs font-semibold text-gray-600">連絡の目的</label>
                    <input type="text" id="ai-topic" value="8/12の練習参加呼びかけ" class="w-full text-sm p-2 border rounded-lg bg-gray-50">
                    
                    <button onclick="generateText()" class="w-full bg-blue-600 text-white font-bold py-2 rounded-lg text-sm shadow hover:bg-blue-700">連絡文を生成する</button>
                    
                    <div id="ai-output" class="hidden bg-gray-50 p-3 rounded-lg border text-xs text-gray-700 whitespace-pre-wrap"></div>
                </div>
            </div>

        </div>

        <!-- ナビゲーションバー -->
        <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around py-2 max-w-md mx-auto shadow-lg">
            <button onclick="switchTab('dashboard')" class="text-center text-blue-600 font-bold" id="nav-dashboard">
                <div class="text-lg">📊</div>
                <div class="text-[10px]">ホーム</div>
            </button>
            <button onclick="switchTab('members')" class="text-center text-gray-400" id="nav-members">
                <div class="text-lg">👥</div>
                <div class="text-[10px]">部員</div>
            </button>
            <button onclick="switchTab('venues')" class="text-center text-gray-400" id="nav-venues">
                <div class="text-lg">🏀</div>
                <div class="text-[10px]">体育館</div>
            </button>
            <button onclick="switchTab('ai')" class="text-center text-gray-400" id="nav-ai">
                <div class="text-lg">🤖</div>
                <div class="text-[10px]">AI連絡</div>
            </button>
        </nav>

        <script>
            function switchTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.getElementById('tab-' + tabName).classList.remove('hidden');
                
                ['dashboard', 'members', 'venues', 'ai'].forEach(name => {
                    const btn = document.getElementById('nav-' + name);
                    if (name === tabName) {
                        btn.className = "text-center text-blue-600 font-bold";
                    } else {
                        btn.className = "text-center text-gray-400";
                    }
                });
            }

            function generateText() {
                const topic = document.getElementById('ai-topic').value;
                const out = document.getElementById('ai-output');
                out.classList.remove('hidden');
                out.innerText = "【AI作成メッセージ】\n\nお疲れ様です！\n" + topic + "についてお知らせです。\n\n日時: 8/12(水) 18:00〜20:00\n場所: 立教大学体育館\n\n参加・欠席の回答をアプリからお願いします！🔥";
            }
        </script>
    </body>
    </html>
    """
