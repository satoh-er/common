# 各方位別 晴天日 全日射量を計算する、グラフ表示、CVSファイルに書き込むプログラム
# calc_clear_sky_insolation.py

################################################################################
import clear_sky_insolation as csi # 各方位別 晴天日 全日射量を計算するモジュール

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
#####################################################################################

def calc_clear_sky(start_t: int, end_t: int, month: int, day: int, Lon:float, Lat: float, tz: int, P: float) -> float: 
    
    """各方位別 晴天日 全日射量を計算

        start_t: 開始時刻、end_t: 終了時刻
        month: 月、day: 日
        Lon: 経度 [deg]、Lat: 緯度 [deg]、tz: 時間ゾーン [h]
        P: 大気透過率

    Returns: 時刻、水平面、各方位別の全日射量の計算結果を返す
        time: 時刻
        全日射量 [W/m2] horizon: 水平面, east: 東面, south: 南面, west: 西面, north: 北面
    """

    # 配列の初期化
    time = np.zeros(((end_t - start_t) + 1))
    horizon = np.zeros(((end_t - start_t) + 1))
    east = np.zeros(((end_t - start_t) + 1))
    south = np.zeros(((end_t - start_t) + 1))
    west = np.zeros(((end_t - start_t) + 1))
    north = np.zeros(((end_t - start_t) + 1))
    i = 0

    # 各時刻の各方位別の全日射量の計算
    for i in range(0, (end_t - start_t) + 1, 1): 
        
        Time_as, B = csi.s_Time_as(month, day, start_t, Lon, tz) # 真太陽時の計算
        sin_h = csi.s_sin_h(Lat, month, day, Time_as, B) # 太陽高度の計算
        A = csi.s_azmth(Lat, month, day, Time_as, B) # 太陽方位角の計算
        #print(A)
        Io = csi.s_Io(month, day) # 大気圏外日射量の計算
        Idn = csi.s_Idn(Io, P, sin_h) # 晴天日 法線面 直達日射量の計算
        s_Isky = csi.s_Isky(Io, P, sin_h, Idn) # 晴天日 水平面 天空日射量の計算
        print(Idn, s_Isky)
        
        time[i] = start_t
        horizon[i] = Idn * csi.s_cos_incident(sin_h, A, 0, 0) + 1 * s_Isky # 水平面の直達日射量と天空日射量の和(晴天日 全日射量)
        east[i] = Idn * csi.s_cos_incident(sin_h, A, 90, -90) + 0.5 * s_Isky # 東面の直達日射量と天空日射量の和(晴天日 全日射量)
        south[i] = Idn * csi.s_cos_incident(sin_h, A, 90, 0) + 0.5 * s_Isky # 南面の直達日射量と天空日射量の和(晴天日 全日射量) 
        west[i] = Idn * csi.s_cos_incident(sin_h, A, 90, 90) + 0.5 * s_Isky # 西面の直達日射量と天空日射量の和(晴天日 全日射量)
        north[i] = Idn * csi.s_cos_incident(sin_h, A, 90, 180) + 0.5 * s_Isky # 北面の直達日射量と天空日射量の和(晴天日 全日射量)

        start_t = start_t + 1 # 時刻の更新

    return time, horizon, east, south, west,north


def plot_graph(g_time: np.ndarray,g_horizon: np.ndarray, g_east: np.ndarray, g_south: np.ndarray, g_west: np.ndarray, g_north: np.ndarray, month: int, day: int, P: float) -> np.ndarray:
    
    """各時刻の各方位別による晴天日 全日射量をグラフ表示する

        g_time: 時刻
        全日射量 [W/m2] g_horizon: 水平面, g_east: 東面, g_south: 南面, g_west: 西面, g_north: 北面
        month: 月、day: 日
        P: 大気透過率
    """

    # 各時刻の各方位別による全日射量をプロット
    plt.plot(g_time, g_horizon, "o-")
    plt.plot(g_time, g_east, "o-")
    plt.plot(g_time, g_south, "o-")
    plt.plot(g_time, g_west, "o-")
    plt.plot(g_time, g_north, "o-")

    # 横軸の設定
    plt.xlabel("時刻", fontsize=16) # 横軸ラベル
    plt.xticks(np.arange(4, 20, 1), fontsize=16) # 横軸目盛りの設定

    # 縦軸の設定
    plt.ylabel("日射量 [W/$\mathrm{m}^{2}$]", fontsize=16) # 縦軸ラベル
    plt.yticks(np.arange(0, 1200, 200), fontsize=16) # 縦軸目盛りの設定

    plt.legend(["水平面", "東面","南面", "西面", "北面"], loc = "upper right", fontsize = 16) # 凡例の設定
    #plt.title("晴天日方位別全日射量", fontsize = 18) #  タイトルの表示
    plt.title("{0} 月 {1} 日  東京の晴天日方位別全日射量 (P = {2})".format(month,day,P), fontsize = 18) #  タイトルの表示

    plt.show() # グラフ表示


def save_to_csv(start_t: int, end_t: int, time: np.ndarray, horizon: np.ndarray, east: np.ndarray, south: np.ndarray, west: np.ndarray, north: np.ndarray) -> np.ndarray:
    
    """各時刻の各方位別による晴天日 全日射量をCSVファイルに保存する

        start_t: 開始時刻、end_t: 終了時刻、time: 時刻
        全日射量 [W/m2] horizon: 水平面, east: 東面, south: 南面, west: 西面, north: 北面
    """
    
    i = 0
    data = np.zeros((((end_t-start_t) + 1), 6)) # 配列の初期化
  
    # 各時刻の各方位別による全日射量を配列に記憶
    for i in range(0, (end_t -start_t) + 1, 1):
            data[i][0] = time[i]
            data[i][1] = horizon[i]
            data[i][2] = east[i]
            data[i][3] = south[i]
            data[i][4] = west[i]
            data[i][5] = north[i]

    np.savetxt("日射量.csv", data, fmt="%.2f", delimiter=',') # 計算結果をcsvに保存
    df = pd.DataFrame(data) # データフレームに変換
    df.to_csv("日射量.csv", index = False, header=["時刻", "水平面", "東面","南面", "西面", "北面"], encoding="Shift-JIS") # ヘッダを追記

if __name__ == '__main__':
    
    start_t = 4 # 開始時刻
    end_t = 19 # 終了時刻
    month = 7 # 月
    day = 21 # 日
    Lon = 139.77 # 経度 [deg]
    Lat = 35.68 # 緯度 [deg]
    tz = 9 # 時間ゾーン [h]
    P = 0.66 # 大気透過率
    
    g_time, g_horizon, g_east, g_south, g_west,g_north = calc_clear_sky(start_t, end_t, month, day, Lon, Lat, tz, P) # 各方位別 晴天日 全日射量を計算
    plot_graph(g_time, g_horizon, g_east, g_south, g_west,g_north, month, day, P) # 各時刻の各方位別による晴天日 全日射量をグラフ表示
    save_to_csv(start_t, end_t, g_time, g_horizon, g_east, g_south, g_west,g_north) # 各時刻の各方位別による晴天日 全日射量をCSVファイルに保存

