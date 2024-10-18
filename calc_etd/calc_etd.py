import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import response_factor as rf

def read_wdc(file_path: str, mode: str, rr: str) -> pd.DataFrame:
    """weadac気象データを読み込む

    Args:
        file_path (str): 読み込むファイルのパス
        mode (str): 暖房の場合は'heating'、冷房の場合は'cooling'
        rr (str): 超過危険率　'1.0%', '2.5%', '10.0%'

    Returns:
        pd.DataFrame: _description_
    """

    if mode == 'heating':
        skiprows = 170
    elif mode == 'cooling':
        skiprows = 192

    # Read the fixed-width file into a DataFrame
    df = pd.read_fwf(
        file_path,
        widths=[11] + [6] * 24, skiprows=skiprows,
        nrows=20,
        header=None,
        encoding='shift-jis'
        ).T
    df = df.drop(0)

    # Set the column names
    df.columns = ['time', 'altitude', 'azimuth', 'wind d.', 'wind v.', 'diret. 1.0%', 'diff. 1.0%', 'temp. 1.0%', 'humid. 1.0%', 'long. 1.0%', 'diret. 2.5%', 'diff. 2.5%', 'temp. 2.5%', 'humid. 2.5%', 'long. 2.5%', 'diret. 10.0%', 'diff. 10.0%', 'temp. 10.0%', 'humid. 10.0%', 'long. 10.0%']
    df = df[['time', 'altitude', 'azimuth', 'wind d.', 'wind v.'] + [col for col in df.columns if rr in col]]
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # ヘッダから超過危険率を削除
    df.columns = df.columns.str.replace(' ' + rr, '')
 
    return df

def calc_sh_sw_ss(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """sh=sin(h)、sw=cos(h)*sin(a)、ss=cos(h)*cos(a)を計算する

    Args:
        df (pd.DataFrame): weadac気象データ

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: _description_
    """

    h = np.radians(df['altitude'].values)
    a = np.radians(df['azimuth'].values)
    # Calculate the solar radiation
    sh = np.sin(h)
    sw = np.cos(h) * np.sin(a)
    ss = np.cos(h) * np.cos(a)

    return sh, sw, ss

def calc_wz_ww_ws(wa: float, wb: float) -> tuple[float, float, float]:
    """Calculate the solar radiation

    Args:
        wa (float): _description_
        wb (float): _description_

    Returns:
        tuple[float, float, float]: _description_
    """

    wz = np.cos(wb)
    ww = np.sin(wa) * np.sin(wb)
    ws = np.cos(wa) * np.sin(wb)

    return wz, ww, ws

if __name__ == '__main__':
    file_path = 'weather_data/12467_KAGOSHIMA.wdc'
    mode = 'cooling'
    rr = '1.0%'
    # WEADAC気象データの読み込み
    df = read_wdc(file_path, mode, rr)

    # 地物反射率の設定
    albedo = 0.2

    # 壁体の吸収率の設定
    a_s = 0.7
    # 屋外側表面熱伝達抵抗
    R_so = 0.04

    # 設計室温
    t_r = 26.0

    # 太陽位置の計算
    sh, sw, ss = calc_sh_sw_ss(df)
    
    # 傾斜面
    wa = np.radians(0)
    wb = np.radians(90)
    wz, ww, ws = calc_wz_ww_ws(wa, wb)
    # 天空の形態係数の計算
    Fs = (1.0 - np.cos(wb)) / 2.0
    # 地面の形態係数の計算
    Fg = 1.0 - Fs

    # 入射角の方向余弦の計算
    # 傾斜面
    cos_theta = np.maximum(wz * sh + ww * sw + ws * ss, 0.0)
    # 水平面
    cos_theta_h = np.maximum(sh, 0.0)

    # 傾斜面日射量の計算
    I_dn = df['diret.'].values
    I_sky = df['diff.'].values
    I_hor = I_dn * sh + I_sky
    slope_I = I_dn * cos_theta + I_sky * Fs + I_hor * albedo * Fg

    # 相当外気温度の計算
    t_o = df['temp.'].values
    t_e = t_o + slope_I * a_s * R_so

    # 壁体の応答係数の計算
    rs = np.array([
        0.11,
        0.05 / 1.6,
        0.04
    ])
    cs = np.array([
        0.0,
        2000.0 * 0.05 * 1000.0,
        0.0
    ])
    a0, _, at, alpha = rf.calc_alpha_matsuo_method(rs=rs, cs=cs, i_max=15)
    cyclic_phi_t = rf.calc_cyclic_response_factor(at=at, alpha=alpha, a0=a0, delta_t=3600)
    _, rft_t, r, _, rft1_t = rf.calc_triangle_response_factor(aa=_, at=at, alpha=alpha, a0=a0, n_max=50, delta_t=3600)
    # 室内表面熱流の計算
    q = np.zeros(24)
    etd = np.zeros(24)
    for n in range(24):
        for j in range(24):
            q[n] += cyclic_phi_t[j] * (t_e[n-j] - t_r)

    # 項別公比法による室内表面熱流の検証
    q_kk = np.zeros(24)
    q_dsh = np.zeros_like(alpha)
    for n in range(365):
        for t in range(24):
            q_kk[t] = (t_e[t] - t_r) * rft_t[0] + np.sum(q_dsh)
            q_dsh = (t_e[t] - t_r) * rft1_t + q_dsh * r
    
    # ETDの計算
    etd = q / a0

    df_result = pd.DataFrame(columns=['time', 't_e-t_r', 'q', 'q_kk', 'etd'])
    df_result['time'] = df['time']
    df_result['t_e-t_r'] = t_e - t_r
    df_result['q'] = q
    df_result['q_kk'] = q_kk
    df_result['etd'] = etd


    # グラフの作成
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # qのグラフ
    ax1.plot(df_result['time'], df_result['q'], label='q')
    ax1.plot(df_result['time'], df_result['q_kk'], label='q_kk')
    ax1.set_xlabel('time')
    ax1.set_ylabel('q')
    ax1.legend()

    # t_e-t_rとetdのグラフ
    ax2.plot(df_result['time'], df_result['t_e-t_r'], label='t_e-t_r')
    ax2.plot(df_result['time'], df_result['etd'], label='etd')
    ax2.set_xlabel('time')
    ax2.set_ylabel('t_e-t_r / etd')
    ax2.legend()

    # グラフの表示
    plt.show()
