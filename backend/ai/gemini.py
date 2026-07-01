# backend/ai/gemini.py
import json
import logging
from google import genai
from google.genai import types

# 從設定檔與提示詞檔引入必要變數
from backend.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from backend.ai.prompt import SYSTEM_PROMPT

# 初始化日誌紀錄器 (取代 print，用於後台靜默記錄錯誤)
logger = logging.getLogger(__name__)

# 初始化 Gemini 客戶端
client = genai.Client(api_key=GEMINI_API_KEY)

def get_route_weights(user_input: str, user_profile: dict, weather_info: str) -> dict:
    """
    接收前端資料與天氣，呼叫 Gemini 進行情境判斷，回傳路網權重 JSON。
    """
    # 建立防呆預設值：若 AI 判斷失敗，則回傳全正常的標準權重，確保系統不崩潰
    fallback_response = {
        "reasoning": "系統暫時無法處理您的文字需求，已為您自動規劃標準路線。",
        "walking_speed_multiplier": 1.0,
        "banned_vehicles": [],
        "weights": {
            "walking": 1.0, "ubike": 1.0, "mrt": 1.0, 
            "bus": 1.0, "train": 1.0, "taxi": 1.0, 
            "scooter": 1.0, "car": 1.0
        }
    }

    # 組裝交給 AI 判斷的上下文資訊
    # 使用 json.dumps 確保字典格式能被轉化為乾淨的字串
    context = f"""
    【使用者生理基礎與資料】：{json.dumps(user_profile, ensure_ascii=False)}
    【即時環境與天氣資訊】：{weather_info}
    【使用者對話與需求】：{user_input}
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=context,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2, # 保持低隨機性，確保權重數值穩定
            )
        )
        
        # 解析並回傳 Dictionary
        return json.loads(response.text)

    except json.JSONDecodeError as e:
        logger.error("Gemini 回傳格式非標準 JSON，解析失敗: %s", str(e))
        return fallback_response
        
    except Exception as e:
        logger.error("呼叫 Gemini API 時發生未知錯誤: %s", str(e))
        return fallback_response