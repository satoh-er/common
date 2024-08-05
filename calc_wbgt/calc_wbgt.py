import math
import numpy as np
from scipy.optimize import fsolve

def calc_wbgt(
        dry_bulb_temperature: float,
        relative_humidity: float,
        velocity: float,
        globe_temperature: float,
        is_sunstrike: bool
        ) -> float:
    """WBGTを計算する
    
    Args:
        dry_bulb_temperature (float): 乾球温度[℃]
        relative_humidity (float): 相対湿度[%]
        velocity (float): 風速[m/s]
        globe_temperature (float): グローブ温度[℃]
        is_sunstrike (bool): 日射が当たる場合はTrue

    Returns:
        float: WBGT[℃]
    """
    natural_wet_bulb_temperature = fsolve(f_natural_wet_bulb_temperature, 20, args=(dry_bulb_temperature, relative_humidity, velocity, globe_temperature))[0]
    
    if is_sunstrike:        # 日射が当たる場合
        wbgt = 0.7 * natural_wet_bulb_temperature + 0.3 * globe_temperature
    else:                   # 日射が当たらない場合
        wbgt = 0.7 * natural_wet_bulb_temperature + 0.2 * globe_temperature + 0.1 * dry_bulb_temperature
    return natural_wet_bulb_temperature, wbgt

def f_natural_wet_bulb_temperature(
        natural_wet_bulb_temperature: float,
        dry_bulb_temperature: float,
        relative_humidity: float,
        velocity: float,
        globe_temperature: float
        ):
    """WBGT計算における湿球温度の関数

    Args:
        natural_wet_bulb_temperature (float): 湿球温度[℃]
        dry_bulb_temperature (float): 乾球温度[℃]
        relative_humidity (float): 相対湿度[%]
        velocity (float): 風速[m/s]
        globe_temperature (float): グローブ温度[℃]

    Returns:
        float: WBGT[℃]
    """
    
    #　グローブ球の平均放射温度を計算
    t_r = calc_average_radiant_temperature(
        globe_temperature=globe_temperature,
        dry_bulb_temperature=dry_bulb_temperature,
        velocity=velocity,
        globe_emissivity=0.95,
        globe_diameter=0.15
    )

    return 4.18 * velocity**0.444 * (dry_bulb_temperature - natural_wet_bulb_temperature) \
        + 1.0e-8 * ((t_r + 273)**4 - (natural_wet_bulb_temperature + 273)**4) \
        - 77.1 * velocity**0.421 * (calc_pas(natural_wet_bulb_temperature) - relative_humidity / 100.0 \
                                    * calc_pas(dry_bulb_temperature=dry_bulb_temperature))

def calc_pas(dry_bulb_temperature: float) -> float:
    """飽和水蒸気圧を計算する（Wexler-Hyland）

    Args:
        dry_bulb_temperature (float): 乾球温度[℃]

    Returns:
        float: 飽和水蒸気圧[kPa]
    """
    
    temp = dry_bulb_temperature + 273
    if dry_bulb_temperature >= 0.01:
        pas = math.exp(- 0.58002206e4 / temp
            + 0.13914993e1
            - 0.48640239e-1 * temp
            + 0.41764768e-4 * temp**2
            - 0.14452093e-7 * temp**3
            + 0.65459673e1 * math.log(temp))
    else:
        pas = math.exp(- 0.56745359e4 / temp
            + 0.63925247e1
            - 0.96778430e-2 * temp
            + 0.62215701e-6 * temp**2
            + 0.20747825e-8 * temp**3
            - 0.94840240e-12 * temp**4
            + 0.41635019e1 * math.log(temp))
    return pas / 1000

def calc_average_radiant_temperature(
        globe_temperature: float,
        dry_bulb_temperature: float,
        velocity: float,
        globe_emissivity: float,
        globe_diameter: float
        ):
    """グローブ球の平均放射温度を計算する

    Args:
        globe_temperature (float): グローブ温度[℃]
        dry_bulb_temperature (float): 乾球温度[℃]
        velocity (float): 風速[m/s]
        globe_emissivity (float): グローブ球の放射率[－]
        globe_diameter (float): グローブ球の直径[m]

    Returns:
        _type_: _description_
    """
    return ((globe_temperature + 273)**4 \
        + 1.1e8 * velocity**0.6 / (globe_emissivity * globe_diameter**0.4) \
            * (globe_temperature - dry_bulb_temperature)) ** 0.25 - 273

if __name__ == "__main__":

    dry_bulb_temperature = np.array([25, 25, 25, 25, 25, 25, 25, 25, 25, 35, 35, 35, 35, 35, 35, 35, 35, 35, 45, 45, 45, 45], dtype=float)
    globe_temperature = np.array([40, 55, 40, 40, 55, 40, 40, 55, 40, 35, 50, 65, 35, 50, 35, 50, 35, 50, 45, 60, 45, 60], dtype=float)
    velocity = np.array([0.3, 0.3, 0.9, 0.3, 0.3, 0.9, 0.3, 0.3, 0.9, 0.3, 0.3, 0.3, 0.9, 0.9, 0.3, 0.3, 0.9, 0.9, 0.3, 0.3, 0.9, 0.9], dtype=float)
    relative_humidity = np.array([20, 20, 20, 50, 50, 50, 80, 80, 80, 20, 20, 20, 20, 20, 50, 50, 50, 50, 20, 20, 20, 20], dtype=float)
    
    wbgt = np.zeros_like(dry_bulb_temperature, dtype=float)
    for i, (t_db, t_g, v, rh) in enumerate(zip(dry_bulb_temperature, globe_temperature, velocity, relative_humidity)):
        t_nw, wbgt[i] = calc_wbgt(t_db, rh, v, t_g, True)
        print(t_db, t_g, v, rh, t_nw, wbgt[i])
    
