from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# ==================== 数据模型（Pydantic） ====================
class Asset(BaseModel):
    """资产数据模型"""
    name: str
    software: str
    category: str
    association: str
    version: str
    file_path: str
    previewUrl: str

class AssetUpdate(BaseModel):
    """资产更新数据模型（与创建相同）"""
    name: str
    software: str
    category: str
    association: str
    version: str
    file_path: str
    previewUrl: str

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

# ==================== API：获取单个资产（READ） ====================
@app.get("/assets/{asset_id}")
def get_asset(asset_id: int):
    """获取单个资产详情"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="资产不存在")
    
    return dict(row)
 
# ==================== API：创建新资产（CREATE） ====================
@app.post("/assets")
def create_asset(asset: Asset):
    """创建新资产"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO assets (name, software, category, association, version, file_path, previewUrl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (asset.name, asset.software, asset.category, asset.association, 
             asset.version, asset.file_path, asset.previewUrl)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return {"id": new_id, "message": "资产创建成功"}
    
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"创建失败: {str(e)}")
 
# ==================== API：更新资产（UPDATE） ====================
@app.put("/assets/{asset_id}")
def update_asset(asset_id: int, asset: AssetUpdate):
    """更新资产信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 先检查资产是否存在
    cursor.execute("SELECT id FROM assets WHERE id = ?", (asset_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="资产不存在")
    
    try:
        cursor.execute(
            """
            UPDATE assets 
            SET name = ?, software = ?, category = ?, association = ?, 
                version = ?, file_path = ?, previewUrl = ?
            WHERE id = ?
            """,
            (asset.name, asset.software, asset.category, asset.association,
             asset.version, asset.file_path, asset.previewUrl, asset_id)
        )
        conn.commit()
        conn.close()
        
        return {"id": asset_id, "message": "资产更新成功"}
    
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"更新失败: {str(e)}")
 
# ==================== API：删除资产（DELETE） ====================
@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: int):
    """删除资产"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 先检查资产是否存在
    cursor.execute("SELECT id FROM assets WHERE id = ?", (asset_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="资产不存在")
    
    try:
        cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
        conn.commit()
        conn.close()
        
        return {"id": asset_id, "message": "资产删除成功"}
    
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")