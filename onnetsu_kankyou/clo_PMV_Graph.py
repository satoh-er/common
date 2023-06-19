#################################################
# 空気温度別による着衣量、PMVを示すグラフ
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

import fslv_calc_PMV_PPD as PMV_Graph

#################################################


def clo_PMV(M: float, var: float, RH: float):

    """ 空気温度別による着衣量、PMVを示すグラフ (clo_PMV_Graph.py)
    M = 1.2 # 代謝量 [met]、var = 0.1、気流 [m/s]、RH = 50 相対湿度 [%]

    """

#####################################################
# 気温 -5℃ の着衣量とPMVとのグラフ
    ta = -5.0 # 空気温度 [℃]
    tmrt = ta # 平均放射温度 [℃]

    PMV_5C = np.zeros((2, 2))
    PMV_5C = [[2.0, 4.0], [0.0, 0.0]]

    for i in range(0,2,1):
        PMV_5C[1][i] = PMV_Graph.PMV(PMV_5C[0][i], M, ta, tmrt, var, RH)
#########################################################
# 気温 0℃ の着衣量とPMVとのグラフ
    ta = 0.0 # 空気温度 [℃]
    tmrt = ta # 平均放射温度 [℃]

    PMV_0C = np.zeros((2, 2))
    PMV_0C = [[2.0, 4.0], [0.0, 0.0]]

    for i in range(0,2,1):
        PMV_0C[1][i] = PMV_Graph.PMV(PMV_0C[0][i], M, ta, tmrt, var, RH)
##########################################################
# 気温 10℃ の着衣量とPMVとのグラフ
    ta = 10.0 # 空気温度 [℃]
    tmrt = ta # 平均放射温度 [℃]

    PMV_10C = np.zeros((4, 4))
    PMV_10C = [[1.0, 1.2, 2.0, 4.0], [0.0, 0.0, 0.0, 0.0]]

    for i in range(0,4,1):
        PMV_10C[1][i] = PMV_Graph.PMV(PMV_10C[0][i], M, ta, tmrt, var, RH)
##########################################################
# 気温 20℃ の着衣量とPMVとのグラフ
    ta = 20.0 # 空気温度 [℃]
    tmrt = ta # 平均放射温度 [℃]

    PMV_20C = np.zeros((6, 6))
    PMV_20C = [[0.3, 0.5, 1.0, 1.2, 2.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

    for i in range(0,6,1):
        PMV_20C[1][i] = PMV_Graph.PMV(PMV_20C[0][i], M, ta, tmrt, var, RH)
##########################################################
# 気温 30℃ の着衣量とPMVとのグラフ
    ta = 30.0 # 空気温度 [℃]
    tmrt = ta # 平均放射温度 [℃]

    PMV_30C = np.zeros((6, 6))
    PMV_30C = [[0.3, 0.5, 1.0, 1.2, 2.0, 4.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

    for i in range(0,6,1):
        PMV_30C[1][i] = PMV_Graph.PMV(PMV_30C[0][i], M, ta, tmrt, var, RH)

#############################################################
# データをプロットする
    plt.plot(PMV_5C[0][:], PMV_5C[1][:], "o-") 
    plt.plot(PMV_0C[0][:], PMV_0C[1][:], "o-")
    plt.plot(PMV_10C[0][:], PMV_10C[1][:], "o-")
    plt.plot(PMV_20C[0][:], PMV_20C[1][:], "o-")
    plt.plot(PMV_30C[0][:], PMV_30C[1][:], "o-")

# 横軸の設定
    plt.xlabel("着衣量 [clo]", fontsize = 16) # 横軸ラベル
    plt.xticks(np.arange(0, 4.5, 0.5), fontsize = 16) # 横軸目盛りの設定

# 縦軸の設定
    plt.ylabel("PMV", fontsize = 16) # 縦軸ラベル
    plt.yticks(np.arange(-3, 4, 1), fontsize = 16) # 縦軸目盛りの設

    plt.title("空気温度別による着衣量とPMVとの関係",fontsize = 16)
    plt.legend(["-5℃", "0℃", "10℃", "20℃", "30℃"], loc = "upper right", fontsize = 16) # 凡例の設定

    plt.show()