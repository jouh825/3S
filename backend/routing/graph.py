# backend/routing/graph.py
import logging
import pandas as pd
import networkx as nx
import osmnx as ox
from scipy.spatial import cKDTree

# 初始化日誌紀錄器，捕捉所有圖資建置過程中的錯誤
logger = logging.getLogger(__name__)

def build_base_osmnx_graph(place_name="Taipei, Taiwan", network_type="all"):
    """
    從 OSMnx 下載並建立基礎路網 Graph (包含街道、人行道等)。
    """
    try:
        # 依照 Notebook 既有邏輯，抓取指定區域的路網
        G = ox.graph_from_place(place_name, network_type=network_type)
        return G
    except Exception as e:
        logger.error("OSMnx 基礎路網載入失敗: %s", str(e))
        raise

def add_transit_nodes_and_edges(G: nx.MultiDiGraph, transit_data: pd.DataFrame, transport_type: str):
    """
    將大眾運輸站點 (捷運、公車、YouBike、台鐵) 加入 Graph，
    並使用 KDTree 將站點空間對位，連接到最近的 OSM 實體路網節點。
    """
    if transit_data.empty:
        logger.warning("載入的 %s 資料為空，跳過該圖層建立。", transport_type)
        return G

    try:
        # 1. 萃取現有 OSM 路網的節點座標，用於建立 KDTree 空間索引
        nodes_gdf = ox.graph_to_gdfs(G, edges=False)
        # OSMnx 預設座標為 (y, x) 即 (緯度, 經度)
        tree = cKDTree(nodes_gdf[['y', 'x']].values) 
        osm_node_ids = nodes_gdf.index.tolist()

        # 2. 迭代大眾運輸資料表，將站點加入 Graph
        for _, row in transit_data.iterrows():
            station_id = f"{transport_type}_{row['node_id']}"
            lat, lon = row['lat'], row['lon']
            
            # 加入站點節點 (標註 type 供後續 Gemini 權重與演算法識別)
            G.add_node(station_id, y=lat, x=lon, type=transport_type, name=row.get('name', 'Unknown'))
            
            # 3. 使用 KDTree 尋找空間上距離最近的實體路網節點 (Nearest Neighbor)
            dist, idx = tree.query([lat, lon], k=1)
            nearest_osm_node = osm_node_ids[idx]
            
            # 4. 建立站點與實體路網的雙向「轉乘/接駁邊緣 (Transfer Edge)」
            # (此處只建立圖論連結與距離，實際時間與票價由 routing.py 與 fare.py 負責)
            G.add_edge(station_id, nearest_osm_node, type='transfer', length=dist)
            G.add_edge(nearest_osm_node, station_id, type='transfer', length=dist)
            
        return G
    
    except Exception as e:
        logger.error("融合 %s 站點與 KDTree 空間連接時發生錯誤: %s", transport_type, str(e))
        raise

def initialize_multi_modal_graph() -> nx.MultiDiGraph:
    """
    系統初始化總樞紐：建立台北市多模式交通 Graph。
    只負責節點、邊緣的融合與建立，不進行任何路徑搜尋。
    """
    try:
        # 1. 建立基礎台北市 OSM 路網
        G = build_base_osmnx_graph(place_name="Taipei, Taiwan", network_type="all")
        
        # ==========================================
        # [⚠️ 需要你修改的地方 ⚠️] 
        # 請將你 Notebook 中使用 pandas 讀取 捷運/公車/YouBike/台鐵 CSV 或 Excel 的程式碼搬移到這裡。
        # 確保清理後的 DataFrame 至少包含這四個欄位：['node_id', 'lat', 'lon', 'name']
        # ==========================================
        
        # 範例：(請以你的真實讀取路徑與變數名稱覆蓋)
        # mrt_data = pd.read_csv("backend/data/mrt_stations.csv")
        # bus_data = pd.read_csv("backend/data/bus_stations.csv")
        # ubike_data = pd.read_csv("backend/data/ubike_stations.csv")
        # tra_data = pd.read_csv("backend/data/tra_stations.csv")
        
        # 這裡暫時建立空 DataFrame 以防伺服器報錯，等你補上真實資料
        mrt_data = pd.DataFrame(columns=['node_id', 'lat', 'lon', 'name'])
        bus_data = pd.DataFrame(columns=['node_id', 'lat', 'lon', 'name'])
        ubike_data = pd.DataFrame(columns=['node_id', 'lat', 'lon', 'name'])
        tra_data = pd.DataFrame(columns=['node_id', 'lat', 'lon', 'name'])
        
        # 2. 利用 KDTree 將四大交通系統精準對位，縫合進實體路網
        G = add_transit_nodes_and_edges(G, mrt_data, transport_type="mrt")
        G = add_transit_nodes_and_edges(G, bus_data, transport_type="bus")
        G = add_transit_nodes_and_edges(G, ubike_data, transport_type="ubike")
        G = add_transit_nodes_and_edges(G, tra_data, transport_type="train")
        
        return G

    except Exception as e:
        logger.critical("Graph 初始化失敗，多模式圖論模型無法建立: %s", str(e))
        raise