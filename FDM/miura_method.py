import numpy as np
from copy import copy
from scipy import interpolate

def miura_method(R: np.ndarray, C: np.ndarray, n_layers: int) -> (np.ndarray, np.ndarray):
    """_summary_

    Args:
        R (float): 熱抵抗[m2･K/W] （順序は室内側→室外側）
        C (float): 熱容量[J/K]
        n_layers: 後退差分で計算する壁体部分（表面熱伝達抵抗を除く）の分割層数
    """

    real_R = copy(R)
    real_R[0] = 0.0
    real_R[len(R) - 1] = 0.0
    real_accume_R = np.cumsum(real_R)
    real_indi_RC = R * C
    real_accume_RC = np.cumsum(real_indi_RC)
    real_C = copy(C)
    real_accume_C = np.cumsum(real_C)
    # RC等分割後の累積RCの計算

    # 差分計算する壁体構成の累積RCの計算
    virtual_accume_RC = np.linspace(min(real_accume_RC), max(real_accume_RC), n_layers + 1)
    # 累積RCと累積Rの関係の曲線を定義
    fitted_curve_R = interpolate.interp1d(real_accume_RC, real_accume_R)
    # RCでの線形補間
    virtual_accume_R = fitted_curve_R(virtual_accume_RC)
    # 累積Rから仮想分割後の各層のRを計算
    virtual_R = np.diff(virtual_accume_R, 1)
    # 室内、室外の熱抵抗を追加
    virtual_R = np.append(np.append(R[0], virtual_R), R[len(R) - 1])

    # 累積Rと累積Cの関係の曲線を定義
    fitted_curve_C = interpolate.interp1d(real_accume_R, real_accume_C)
    # 累積Rに相当する累積Cを線形補間から求める
    virtual_accume_C = fitted_curve_C(virtual_accume_R)

    # 差分計算する格子点の熱容量の設定
    # total_C = np.sum(C)
    # virtual_C = np.full(len(virtual_R) - 1, fill_value=total_C / float(n_layers))
    # virtual_C[0] = total_C / float(n_layers) / 2.0
    # virtual_C[n_layers] = total_C / float(n_layers) / 2.0
    virtual_C = np.zeros(n_layers + 1)
    for i in range(1, n_layers):
        virtual_C[i] = (virtual_accume_C[i+1] - virtual_accume_C[i-1]) / 2.0
    virtual_C[0] = virtual_accume_C[1] / 2.0
    virtual_C[n_layers] = (virtual_accume_C[n_layers] - virtual_accume_C[n_layers-1]) / 2.0

    return (virtual_R, virtual_C)


if __name__ == "__main__":

    # 壁体構成の定義
    R = np.array([0.125, 0.750, 0.140, 0.050])  # 抵抗値
    C = np.array([0.0, 0.75, 96.0, 0.0])  # 容量値

    # 壁体内の分割数
    n_layers = 2

    virtual_R, virtual_C = miura_method(R=R, C=C, n_layers=n_layers)
