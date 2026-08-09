from typing import List
from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.database import init_db, get_session
from app.models import Member, Practice, Venue

app = FastAPI(title="RUB Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Circle OS API is fully online!"}

# --- データベース操作 API ---

@app.post("/members/add")
def add_member(
    name: str = Form(...),
    grade: int = Form(...),
    position: str = Form(...),
    session: Session = Depends(get_session)
):
    new_member = Member(name=name, grade=grade, position=position)
    session.add(new_member)
    session.commit()
    return RedirectResponse(url="/app?tab=members", status_code=303)

@app.post("/members/delete/{member_id}")
def delete_member(member_id: int, session: Session = Depends(get_session)):
    member = session.get(Member, member_id)
    if member:
        session.delete(member)
        session.commit()
    return RedirectResponse(url="/app?tab=members", status_code=303)

# --- フロントエンド画面 ---

@app.get("/app", response_class=HTMLResponse)
def get_ui(tab: str = "dashboard", session: Session = Depends(get_session)):
    members = session.exec(select(Member)).all()
    member_count = len(members)
    
    # 部員一覧リストの動的生成
    members_html = ""
    if not members:
        members_html = '<p style="text-align:center; color:#888; font-size:12px; padding:16px 0;">登録された部員はいません。上のフォームから追加してください。</p>'
    else:
        for m in members:
            members_html += f"""
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee; padding:8px 0;">
                <div>
                    <strong>{m.name}</strong> <span style="font-size:12px; color:#666;">({m.grade}年/{m.position})</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:11px; background:#e6f4ea; color:#137333; padding:2px 6px; border-radius:4px;">{m.payment_status}</span>
                    <form action="/members/delete/{m.id}" method="post" style="margin:0;">
                        <button type="submit" style="color:#d93025; font-weight:bold; border:none; background:none; cursor:pointer; font-size:12px;">削除</button>
                    </form>
                </div>
            </div>
            """

    return f"""
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
            
            <header class="bg-blue-600 text-white p-4 rounded-xl shadow flex justify-between items-center">
                <h1 class="text-xl font-bold">RUB Manager</h1>
                <span class="text-xs bg-blue-500 px-2 py-1 rounded">DB Live</span>
            </header>

            <!-- 📊 ホーム -->
            <div id="sec-dashboard" class="space-y-4 {'block' if tab == 'dashboard' else 'hidden'}">
                <section class="bg-white p-4 rounded-xl shadow border border-gray-100">
                    <h2 class="text-sm font-semibold text-gray-500 mb-2">次回練習・AI予測</h2>
                    <div class="text-lg font-bold text-blue-600 mb-1">8/12 18:00〜20:00</div>
                    <div class="text-xs text-gray-600 mb-3">場所: 立教大学体育館</div>
                    <div class="bg-blue-50 p-3 rounded-lg border border-blue-100 flex justify-between items-center">
                        <div>
                            <div class="text-xs text-gray-500">AI参加予測人数</div>
                            <div class="text-2xl font-extrabold text-blue-800">{member_count} 人</div>
                        </div>
                        <div class="text-right">
                            <div class="text-xs text-gray-500">信頼度</div>
                            <div class="text-sm font-bold text-green-600">88%</div>
                        </div>
                    </div>
                </section>

                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-white p-3 rounded-xl shadow text-center">
                        <div class="text-xs text-gray-500">登録部員数</div>
                        <div class="text-xl font-bold">{member_count} 名</div>
                    </div>
                    <div class="bg-white p-3 rounded-xl shadow text-center">
                        <div class="text-xs text-gray-500">平均参加率</div>
                        <div class="text-xl font-bold text-green-600">82%</div>
                    </div>
                </div>
            </div>

            <!-- 👥 部員管理 -->
            <div id="sec-members" class="space-y-3 {'block' if tab == 'members' else 'hidden'}">
                <h2 class="text-md font-bold text-gray-700">部員登録 & 一覧 ({member_count}名)</h2>
                
                <form action="/members/add" method="post" class="bg-white p-3 rounded-xl shadow space-y-2">
                    <div class="text-xs font-bold text-gray-600">新規部員を追加</div>
                    <div class="grid grid-cols-3 gap-2">
                        <input type="text" name="name" placeholder="名前" required class="text-xs p-2 border rounded bg-gray-50">
                        <input type="number" name="grade" placeholder="学年" min="1" max="4" required class="text-xs p-2 border rounded bg-gray-50">
                        <input type="text" name="position" placeholder="ポジ" required class="text-xs p-2 border rounded bg-gray-50">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 text-white font-bold py-1.5 rounded text-xs">追加保存</button>
                </form>

                <div class="bg-white p-4 rounded-xl shadow space-y-1">
                    {members_html}
                </div>
            </div>

            <!-- 🏀 体育館管理 -->
            <div id="sec-venues" class="space-y-3 {'block' if tab == 'venues' else 'hidden'}">
                <h2 class="text-md font-bold text-gray-700">体育館施設一覧</h2>
                <div class="bg-white p-3 rounded-xl shadow border-l-4 border-blue-500">
                    <div class="font-bold">立教大学体育館</div>
                    <div class="text-xs text-gray-500">料金: 12,000円 | 定員: 80人 | 池袋</div>
                </div>
            </div>

            <!-- 🤖 AI連絡 -->
            <div id="sec-ai" class="space-y-3 {'block' if tab == 'ai' else 'hidden'}">
                <h2 class="text-md font-bold text-gray-700">🤖 AI連絡文作成</h2>
                <div class="bg-white p-4 rounded-xl shadow space-y-3">
                    <input type="text" id="ai-topic" value="8/12の練習参加呼びかけ" class="w-full text-sm p-2 border rounded-lg bg-gray-50">
                    <button type="button" onclick="generateText()" class="w-full bg-blue-600 text-white font-bold py-2 rounded-lg text-sm">連絡文を生成</button>
                    <div id="ai-output" class="hidden bg-gray-50 p-3 rounded-lg border text-xs text-gray-700 whitespace-pre-wrap"></div>
                </div>
            </div>

        </div>

        <!-- ナビゲーションバー -->
        <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around py-2 max-w-md mx-auto shadow-lg z-50">
            <button type="button" onclick="showTab('dashboard')" class="text-center {'text-blue-600 font-bold' if tab == 'dashboard' else 'text-gray-400'}" id="btn-dashboard">
                <div class="text-lg">📊</div>
                <div class="text-[10px]">ホーム</div>
            </button>
            <button type="button" onclick="showTab('members')" class="text-center {'text-blue-600 font-bold' if tab == 'members' else 'text-gray-400'}" id="btn-members">
                <div class="text-lg">👥</div>
                <div class="text-[10px]">部員</div>
            </button>
            <button type="button" onclick="showTab('venues')" class="text-center {'text-blue-600 font-bold' if tab == 'venues' else 'text-gray-400'}" id="btn-venues">
                <div class="text-lg">🏀</div>
                <div class="text-[10px]">体育館</div>
            </button>
            <button type="button" onclick="showTab('ai')" class="text-center {'text-blue-600 font-bold' if tab == 'ai' else 'text-gray-400'}" id="btn-ai">
                <div class="text-lg">🤖</div>
                <div class="text-[10px]">AI連絡</div>
            </button>
        </nav>

        <script>
            function showTab(name) {{
                ['dashboard', 'members', 'venues', 'ai'].forEach(t => {{
                    const sec = document.getElementById('sec-' + t);
                    const btn = document.getElementById('btn-' + t);
                    if (sec && btn) {{
                        if (t === name) {{
                            sec.classList.remove('hidden');
                            sec.classList.add('block');
                            btn.className = 'text-center text-blue-600 font-bold';
                        }} else {{
                            sec.classList.add('hidden');
                            sec.classList.remove('block');
                            btn.className = 'text-center text-gray-400';
                        }}
                    }}
                }});
            }}

            function generateText() {{
                const topic = document.getElementById('ai-topic').value;
                const out = document.getElementById('ai-output');
                out.classList.remove('hidden');
                out.innerText = "【AI作成メッセージ】\\n\\nお疲れ様です！\\n" + topic + "についてお知らせです。\\n\\n日時: 8/12(水) 18:00〜20:00\\n場所: 立教大学体育館\\n\\n回答をお願いします！🔥";
            }}
        </script>
    </body>
    </html>
    """
