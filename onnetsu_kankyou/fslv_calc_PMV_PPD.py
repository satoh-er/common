################################################
# PMV、PPD を計算するプログラム fslv_calc_PMV_PPD.py
# fsolveで着衣表面温度 tcl を求める
################################################

import math
import scipy.optimize as opt

def P_fs(T: float) -> float :
    """ 飽和水蒸気圧計算 Wexler・Hylandの式
    Args:
        T: 温度 [℃]

    Returns:
        P_fs: 飽和水蒸気圧 [kPa] を返す
    """
    Tabs=T+273.15 # 絶対温度に変換
    
    if T>0:
        Pws=math.exp(-5800.2206 / Tabs + 1.3914993 + Tabs * (-0.048640239 + Tabs * (0.000041764768 - 0.000000014452093 * Tabs)) + 6.5459673 * math.log(Tabs))
    else:
        Pws=math.exp(-5674.5359 / Tabs + 6.3925247 + Tabs * (-0.009677843 + Tabs * (0.00000062215701 + Tabs * (2.0747825E-09 - 9.484024E-13 * Tabs))) + 4.1635019 * math.log(Tabs))
    
    P_fs=Pws/1000
    
    return P_fs

def P_ftr(T: float, RH: float) -> float :
    """ 水蒸気圧の計算

    Args:
        T: 温度 [℃]
        RH: 相対温度 [%]

    Returns:
        P_ftr: 水蒸気圧 [kPa] を返す
    """
    P_ftr = RH * P_fs(T) / 100
    
    return P_ftr


def tcl_f(tcl: float, Icl: float, ta: float, tmrt: float, QM: float, fcl: float, hcf: float) -> float:
    """着衣表面温度 tcl を求める

    Args:
        tcl: 着衣表面温度 [℃]、Icl: 着衣量 [clo]、ta: 空気温度 [℃]、tmrt: 平均放射温度 [℃]、QM: 代謝量 [W/m2]
        fcl: 着衣表面積係数、hcf : hcの判定に必要 → 12.1 * math.sqrt(気流)

    Returns:
        tcl: 着衣表面温度 [℃] を返す 
    """

    if (2.38 * (tcl - ta) ** 0.25) > hcf: # hc: 着衣表面対流熱伝達率 [W/m2K]
        hc = 2.38 * (tcl - ta) ** 0.25 
    else:
        hc = hcf

    return 35.7 - 0.028 *QM - 0.155 * Icl * ((3.96 * 10 ** -8) * fcl * ((tcl + 273) ** 4 - (tmrt + 273) ** 4) + fcl * hc * (tcl -ta)) - tcl

def PMV(Icl: float, M: float, ta: float, tmrt: float, var: float, RH: float) -> float:

    """PMV 予想平均申告の計算

    Args:
        Icl: 着衣量 [clo], M: 代謝量 [met], ta: 空気温度 [℃], tmrt: 平均放射温度 [℃], var: 気流 [m/s], RH: 相対湿度 [%]
    Returns:
        PMV_Data: PMVの値を返す
    """

    Pa = P_ftr(ta, RH) * 1000 # 水蒸気圧の計算 [Pa]

    Mw = 0
    QM = (M - Mw) * 58.15 # 代謝量 [W/m2]

    if Icl < 0.5: # fcl: 着衣表面積係数
        fcl = 1.00 + 0.2 * Icl
    else:
        fcl = 1.05 + 0.1 * Icl

    hcf = 12.1 * math.sqrt(var)

    tcl = ta # 着衣表面温度初期値
    tcl = opt.fsolve(tcl_f, tcl, args = (Icl, ta, tmrt, QM, fcl, hcf)) # 着衣表面温度 tcl を求める
    
    if (2.38 * (tcl - ta) ** 0.25) > hcf: # hc: 着衣表面対流熱伝達率 [W/m2K]
        hc = 2.38 * (tcl - ta) ** 0.25 
    else:
        hc = hcf
    
    # PMV計算
    PMV_Data = (0.303* math.exp(-0.036 * QM) + 0.028) * (QM - (3.05 * 10 ** -3) * (5733 - 6.99 * QM - Pa) - 0.42 * (QM - 58.15) - (1.7 * 10 ** -5) * QM * (5867 - Pa) - 0.0014 * QM * (34 - ta) - (3.96 * 10 ** -8) * fcl * ((tcl + 273) ** 4 - (tmrt + 273) ** 4) - fcl * hc * (tcl - ta))
    return float(PMV_Data)

def PPD(PMV_Data: float) -> float:

    """ PPD 予想不満足者率の計算

    Args:
        PMV_Data: PMV

    Returns:
        PPD_Data: PPDの値を返す
    """
    PPD_Data = 100 - 95 * math.exp(-0.03353 * PMV_Data ** 4 - 0.2179 * PMV_Data ** 2) # PPD 計算

    return float(PPD_Data)


 