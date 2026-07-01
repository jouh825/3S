# backend/config.py
import os
from pathlib import Path

# ==========================================
# 1. API 金鑰 (嚴格從環境變數/GitHub Secrets 讀取)
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
MOENV_API_KEY = os.environ.get("MOENV_API_KEY")

# 預留交通部 TDX API 金鑰 (未來里程碑會用到)
TDX_APP_ID = os.environ.get("TDX_APP_ID")
TDX_APP_KEY = os.environ.get("TDX_APP_KEY")

# 安全防護：核心大腦金鑰若遺失，直接阻擋系統啟動
if not GEMINI_API_KEY:
    raise ValueError("❌ 嚴重錯誤：找不到 GEMINI_API_KEY。請確認已設定環境變數或 GitHub Secrets！")

# ==========================================
# 2. 模型與參數設定
# ==========================================
# 允許透過環境變數動態切換模型，若無則預設使用 3.5-flash
GEMINI_MODEL_NAME = GEMINI_MODEL_NAME = "gemini-3.5-flash"

# ==========================================
# 3. 專案路徑設定 (動態定位，避免跨平台路徑錯誤)
# ==========================================
# BASE_DIR 會自動定位到專案的最外層目錄 (3S_Route_AI/)
BASE_DIR = Path(__file__).resolve().parent.parent

# 統一管理資料夾路
DATA_DIR = os.path.join(BASE_DIR, 'backend', 'data')

# 地圖檔案的路徑 (允許從環境變數覆寫，否則讀取預設的 data 資料夾)
GRAPH_FILE_PATH = os.environ.get("GRAPH_FILE_PATH", os.path.join(DATA_DIR, "taipei_network.graphml"))

# ==========================================
# 4. 系統常數
# ==========================================
DEFAULT_CITY = "臺北市"