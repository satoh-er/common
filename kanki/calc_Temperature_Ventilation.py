##################################################################################
# 温度差換気より室外の温度差と換気量を計算、プロット、csvファイルに保存するプログラム
#  calc_Temperature_Ventilation.py
##################################################################################

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

def Opening_Area_Parallel(a1: float,A1: float,a2: float,A2: float) -> float:

    """合成開口面積の計算 (並列)
        a1, a2: 流量係数
        A1, A2: 開口部面積 [m^2]

    Returns:
        a_A: 合成開口面積 [m^2] の値を返す 
    """
    
    a_A = a1 * A1 + a2 * A2 # 合成開口面積の計算 (並列)
    return a_A

def Opening_Area_Serise(a1: float,A1: float,a2: float,A2: float) -> float:

     """合成開口面積の計算 (直列)
        a1, a2: 流量係数
        A1, A2: 開口部面積 [m^2]

    Returns:
        a_A: 合成開口面積 [m^2] の値を返す 
    """
     
     a_A = 1/(math.sqrt(pow(1/(a1 * A1),2) + pow(1/(a1 * A1),2))) # 合成開口面積の計算 (直列)
     return a_A

def calc_Ventilation(a_A: float, h: float, t_i:float, t_o: float) -> float :

    """温度差換気の計算
        a_A: 合成開口面積 [m^2]
        h: 流入を流出の高低差 [m]
        t_i: 室内の温度 [℃]
        t_o: 室外の温度 [℃]
    Returns:
        Q: 換気量 [m^3/sec] の値を返す
    """
    g = 9.8 # 重力加速度 [m/s^2]
    Q = a_A * math.sqrt((2 * g * h * (t_i - t_o)) / (273 + t_i)) #温度差換気の計算

    return Q


def Plot_Data(a1: float, a2: float, A1: float, A2: float, h: float, t_i: float, t_o: float, delta_temp: float, t_i_end: float) -> np.array:

    """室内外の温度差が0～30℃あるときの換気量 Q を計算
        a1, a2: 流量係数
        A1, A2: 開口部面積 [m^2]
        h: 流入を流出の高低差 [m]
        t_i: 室内の温度 [℃]
        t_o: 室外の温度 [℃]
        delta_temp: グラフをプロットする際の温度差の間隔 [℃]
        t_i_end: 室内温度の上限値 [℃]

    Returns:
        data[i][0]: 温度差 [℃]、data[i][1]: 換気量 [m^3/h] の値を返す

    """
    a_A = Opening_Area_Serise(a1, A1, a2, A2) # 合成開口面積の計算 (直列)

    data = np.zeros(((int(t_i_end / delta_temp) + 1), 2)) # 配列の初期化
    

    for i in range(0, (int(t_i_end / delta_temp) + 1), 1): # 室内外の温度差が0～30℃までの換気量を計算
        Q = calc_Ventilation(a_A, h, t_i, t_o) # 温度差換気の計算

        data[i][0] = t_i
        data[i][1] = Q * 3600 # 1秒当たりから1時間当たりの換気量に変換 Q [m^3/h]
        t_i = t_i + delta_temp
    
    return data # data[i][0]: 温度差 [℃]、data[i][1]: 換気量 [m^3/h] の値を返す
    

def Plot_Graph(data: np.array):

    """室内外の温度差と換気量のグラフを表示させる
        data[i][0]: 温度差[℃]、data[i][1]: 換気量[m^3/h]
    """

    plt.plot(data[:,0],data[:,1], "o-") # データをプロットする

    # 横軸の設定
    plt.xlabel("室内外温度差 Δt [℃]", fontsize = 16) # 横軸ラベル
    plt.xticks(np.arange(0, 35, 5), fontsize = 16) # 横軸目盛りの設定

    # 縦軸の設定
    plt.ylabel("換気量 Q [$\mathrm{m}^{3}$ / h]", fontsize = 16) # 縦軸ラベル
    plt.yticks(np.arange(0, 45000, 5000), fontsize = 16) # 縦軸目盛りの設定

    plt.title("温度差換気による室内外の温度差と換気量のグラフ (室外温度は0 ℃ で固定)", fontsize = 16) #  タイトルの表示

    plt.show() # グラフ表示する

def Save_to_csv(csv_data: np.array):
    df = pd.DataFrame(csv_data)
    df.to_csv("換気量.csv", index = False, header=["室内外温度差 Δt [℃]", "換気量 Q [m^3/h]"], encoding="Shift-JIS")


if __name__ == '__main__':
    
    print()
