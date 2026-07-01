# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS

# 先預留未來要從其他資料夾引入的函式 (目前先註解掉，等我們寫到那邊再打開)
# from backend.ai.gemini import get_route_weights
# from backend.routing.graph import load_graph
# from backend.routing.routing import calculate_best_path
# from backend.routing.fare import calculate_total_fare

app = Flask(__name__)
CORS(app) # 允許前端跨域請求

# (未來預留) 伺服器啟動時，先載入地圖檔案到記憶體，不用每次都重抓
# G = load_graph() 

@app.route('/api/route', methods=['POST'])
def get_route():
    try:
        # 1. 接收前端傳來的資料 (生理數據、對話、起終點)
        data = request.json
        user_input = data.get('user_input', '')
        user_profile = data.get('user_profile', {})
        source_node = data.get('source', '')
        target_node = data.get('target', '')

        # --- 以下是未來要串接的邏輯，目前先放上假資料測試 API 是否暢通 ---
        
        # 2. 呼叫 Gemini 取得權重 (未來實作)
        # decision = get_route_weights(user_input, user_profile)
        
        # 3. 呼叫 NetworkX 運算路線 (未來實作)
        # best_path = calculate_best_path(G, source_node, target_node, decision)
        
        # 4. 呼叫計價系統 (未來實作)
        # fare = calculate_total_fare(G, best_path, user_profile.get('identity'))

        # 模擬運算結果 (最小更動測試用)
        mock_response = {
            "status": "success",
            "reasoning": "這是測試用的 AI 導遊回應：已經收到您的需求！",
            "path": ["A", "B", "C"], # 假路線
            "fare": 50               # 假票價
        }

        return jsonify(mock_response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # 啟動伺服器，設定 port 為 5000
    app.run(debug=True, host='0.0.0.0', port=5000)