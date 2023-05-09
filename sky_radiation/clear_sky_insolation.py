# 各方位別 晴天日 全日射量を計算するモジュール　clear_sky_insolation.py

#################################################
import math
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

#################################################

def s_ETime(month: int, day: int) -> float:

    """均時差 [h]の計算
        month: 月、day: 日
    Returns:
        B:
        E: 均時差を返す
        n: 元旦からの日数を返す
    """
    # 元旦からの日数計算
    dt1 = datetime(2023-1,12,31)
    dt2 = datetime(2023,month,day)
    n = (dt2 - dt1)


    B = (360 * (n.days - 81)) / 365
    E = 0.1645 * math.sin(math.radians(2 * B)) - 0.1255 * math.cos(math.radians(B)) - 0.025 * math.sin(math.radians(B))
    return B, E, n

def s_Time_as(month: int, day: int, time: int, Lon: float,tz: int) -> float:

    """真太陽時の計算
        month: 月、day: 日、time: 標準時 [h]
        Lon: 経度 [deg]、tz: 時間ゾーン [h]
    Returns:
        Time_as: 真太陽時 [h] の計算結果を返す
    """
    B,E,n = s_ETime(month, day)
    Time_as = time + E + (Lon - tz * 15) / 15 # 真太陽時の計算
    return Time_as, B

def s_sin_decl(B: float) -> float:

    """太陽赤緯の計算
        B:
    Returns:
        sin_decl: 太陽赤緯の計算結果を返す
    """
    sin_decl = 0.397949 * math.sin(math.radians(B)) # 太陽赤緯の計算
    return sin_decl

def s_sin_h(Lat: float, month: int, day: int, Time_as: float, B:float) -> float :

    """太陽高度の計算
        Lat: 緯度 [deg]、moth: 月、day: 日
        Time_as: 真太陽時 [h]
    Returns:
        sin_h: 太陽高度 [rad] の計算結果を返す
    """
    sin_h = math.sin(math.radians(Lat)) * s_sin_decl(B) + math.cos(math.radians(Lat)) * math.cos(math.asin(s_sin_decl(B))) * math.cos(math.radians((Time_as -12) * 15)) # 太陽高度の計算
    
    if(sin_h < 0): # 太陽高度がマイナスのとき
        sin_h = 0
    
    return sin_h

def s_azmth(Lat: float, month: int, day: int, Time_as: float, B:float) -> float:

    """太陽方位角の計算
        Lat: 緯度 [deg]、moth: 月、day: 日
        Time_as: 真太陽時 [h]
    Returns:
        A: 太陽方位角 [rad] の計算を返す
    """
    sin_h = s_sin_h(Lat, month, day, Time_as, B) # 太陽高度 sin_h

    if(sin_h > 0):
        cos_A = (sin_h * math.sin(math.radians(Lat)) - s_sin_decl(B)) / (math.sqrt(1 - sin_h * sin_h) * math.cos(math.radians(Lat))) # 太陽方位角の計算
        if (abs(abs(cos_A) - 1)) < 0.000001:
            if(Lat > 0):
                A = 0
            else:
                A = math.pi()
        else:
            A = (math.acos(cos_A)) * np.sign(Time_as - 12) # 午後のとき
            #print(Time_as) 
    else:
        A = 0 
    
    return A 

def s_Io(month: int, day: int) -> float:

    """大気圏外日射量の計算
        moth: 月、day: 日

    Returns:
        Io: 大気圏外日射量 [W/m2] の計算を返す
    """
    B,E,n = s_ETime(month, day) # 元旦からの日数を返す
    Io = 1382 * (1 + 0.033 * math.cos(2 * math.pi * n.days / 365)) # 大気圏外日射量の計算

    return Io

def s_Idn(Io: float, P: float, sin_h: float) -> float:

    """晴天日 法線面 直達日射量の計算
        Io: 大気圏外日射量 [W/m2]、P: 大気透過率、sin_h: 太陽高度 [rad]
    Returns:
        Idn: 晴天日 法線面 直達日射量 [W/m2] の計算量を返す
    """
    if (sin_h > 0):
        Idn = Io * (math.pow(P,(1/sin_h))) # 晴天日 法線面 直達日射量の計算(ブーゲの式)
    else:
        Idn = 0 # 太陽高度がマイナスのとき

    return Idn

def s_Isky(Io: float, P:float, sin_h: float, I_dn: float) -> float:

    """晴天日 水平面 天空日射量の計算
        Io: 大気圏外日射量 [W/m2]、P: 大気透過率、sin_h: 太陽高度 [rad]
        I_dn: 晴天日 法線面 直達日射量 [W/m2] 
    Returns:
        I_sky: 晴天日 水平面 天空日射量 [W/m2] の計算量を返す
    """
    if(sin_h > 0):
        I_sky = (Io - I_dn) * sin_h * ((0.66 - 0.32 * sin_h) * (0.5 + (0.4 - 0.3 * P) * sin_h)) # 晴天日 水平面 天空日射量の計算
    else: # 太陽高度がマイナスのとき
        I_sky = 0 

    return I_sky

def s_cos_incident(sin_h: float, A: float, Wtilt: float, Wazm:float) -> float:

    """傾斜面の太陽光入射角の計算
        sin_h: 太陽高度 [rad]、A: 太陽方位角 [rad]、Wtilt: 傾斜面傾斜角 [deg]、Wazm: 傾斜面方位角 [deg] 

    Returns:
        cos_incident: 傾斜面の太陽光入射角の計算の結果を返す
    """
    if(sin_h > 0):
        cos_incident = math.cos(math.radians(Wtilt)) * sin_h + math.sin(math.radians(Wtilt)) * math.sqrt(1 - sin_h * sin_h) * math.cos(A-math.radians(Wazm)) # 傾斜面の太陽光入射角の計算
        if(cos_incident < 0): # 傾斜面の太陽光入射角がマイナスのとき
            cos_incident = 0
    else: # 太陽高度がマイナスのとき
        cos_incident = 0 
    
    return cos_incident