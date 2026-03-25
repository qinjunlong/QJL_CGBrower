from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
# ==================== 数据库连接 ====================
def get_db():
    conn = sqlite3.connect("cg_assets.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==================== CORS 中间件 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 挂载静态文件目录 ====================
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="static/img"), name="img")
app.mount("/video", StaticFiles(directory="static/video"), name="video")
# ==================== 路由：根路径返回 index.html ====================
@app.get("/")
def read_root():
    """
    返回静态文件夹中的 index.html
    """
    return FileResponse("static/index.html")

# ==================== API：获取资产数据 ====================
@app.get("/assets")
def get_assets():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()

    assets = [dict(row) for row in rows]

    conn.close()

    return assets