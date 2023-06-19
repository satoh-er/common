#################################################
# 気流別による空気温度とPMVを示すグラフ
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

import fslv_calc_PMV_PPD as ta_PMV_Graph

#################################################

def ta_var_PMV(M: float, Icl: float, RH: float):

    """気流別による空気温度、PMV を示すグラフ (ta_var_PMV.py)
    M = 1.2 # 代謝量 [met]、着衣量 = 1.0 [met]、RH = 50 相対湿度 [%]    

    """
####################################################
# 気流 0.1 m/sec のとき、空気温度とPMVとのグラフ
    var = 0.1
    var_01m = np.zeros((2,11))

    var_01m[0][0] = 10
    for i in range(0, 11, 1):
        var_01m[1][i] = ta_PMV_Graph.PMV(Icl, M, var_01m[0][i], var_01m[0][i], var, RH)

        if(i < 10):
            var_01m[0][i+1] = var_01m[0][i] + 2
        
####################################################
# 気流 0.2 m/sec のとき、空気温度とPMVとのグラフ
    var = 0.2
    var_02m = np.zeros((2,11))

    var_02m[0][0] = 10
    for i in range(0, 11, 1):
        var_02m[1][i] = ta_PMV_Graph.PMV(Icl, M, var_02m[0][i], var_02m[0][i], var, RH)

        if(i < 10):
            var_02m[0][i+1] = var_02m[0][i] + 2

######################################################
# 気流 0.5 m/sec のとき、空気温度とPMVとのグラフ
    var = 0.5
    var_05m = np.zeros((2,10))

    var_05m[0][0] = 12
    for i in range(0, 10, 1):
        var_05m[1][i] = ta_PMV_Graph.PMV(Icl, M, var_05m[0][i], var_05m[0][i], var, RH)

        if(i < 9):
            var_05m[0][i+1] = var_05m[0][i] + 2

######################################################
# 気流 1.0 m/sec のとき、空気温度とPMVとのグラフ
    var = 1.0
    var_1m = np.zeros((2,9))

    var_1m[0][0] = 14
    for i in range(0, 9, 1):
        var_1m[1][i] = ta_PMV_Graph.PMV(Icl, M, var_1m[0][i], var_1m[0][i], var, RH)

        if(i < 8):
            var_1m[0][i+1] = var_1m[0][i] + 2

######################################################
# 気流 2.0 m/sec のとき、空気温度とPMVとのグラフ
    var = 2.0
    var_2m = np.zeros((2,9))

    var_2m[0][0] = 14
    for i in range(0, 9, 1):
        var_2m[1][i] = ta_PMV_Graph.PMV(Icl, M, var_2m[0][i], var_2m[0][i], var, RH)

        if(i < 8):
            var_2m[0][i+1] = var_2m[0][i] + 2

#############################################################
# データをプロットする
    plt.plot(var_01m[0][:], var_01m[1][:], "o-") 
    plt.plot(var_02m[0][:], var_02m[1][:], "o-")
    plt.plot(var_05m[0][:], var_05m[1][:], "o-")
    plt.plot(var_1m[0][:], var_1m[1][:], "o-")
    plt.plot(var_2m[0][:], var_2m[1][:], "o-")

# 横軸の設定
    plt.xlabel("空気温度 [℃]", fontsize = 16) # 横軸ラベル
    plt.xticks(np.arange(10, 35, 5), fontsize = 16) # 横軸目盛りの設定

# 縦軸の設定
    plt.ylabel("PMV", fontsize = 16) # 縦軸ラベル
    plt.yticks(np.arange(-3, 4, 1), fontsize = 16) # 縦軸目盛りの設

    plt.title("気流別による空気温度とPMVとの関係",fontsize = 16)
    plt.legend(["0.1 [m/sec]", "0.2 [m/sec]", "0.5 [m/sec]", "1.0 [m/sec]", "2.0 [m/sec]"], loc = "upper left", fontsize = 16) # 凡例の設定

    plt.show()


