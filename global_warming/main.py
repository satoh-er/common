import pandas as pd
import requests
import datetime
from dateutil.relativedelta import relativedelta
import time
import csv
import urllib.request
from bs4 import BeautifulSoup
import re

def download_txt(url: str, file_name: str):
    """放射量気象データをファイルに保存する

    Args:
        url (str): 収集する気象データのURL
        file_name (str): 保存するテキストファイル名
    """
    response = requests.get(url)
    response.encoding = response.apparent_encoding

    with open(file='out/' + file_name, mode='w', newline='\n', encoding='utf-8') as file:

        file.write(response.text)


def download_downward_radiation():
    """指定する期間の放射量気象データを取得する。
        館野の下向き赤外放射量が対象となる。（url_baseを変更することで気象要素の変更が可能）
        地点を変更するときは、url = ・・・・ + '_xxx.txt' のxxxを変更する
    """
    
    ds = datetime.date(1993, 1, 1)
    de = datetime.date(2023, 5, 1)

    url_base = 'https://www.data.jma.go.jp/gmd/env/radiation/data/geppo/' 

    # 開始日から終了日まで月ごとにループ
    current_date = ds
    while current_date <= de:
        # 連続で実行するとサーバに負荷がかかるので、1秒停止する
        time.sleep(1)
        print(current_date.strftime("%Y-%m"))

        date_str = str(current_date.year).zfill(4) + str(current_date.month).zfill(2)
        url = url_base + date_str + '/DL' + date_str + '_tat.txt'

        download_txt(url=url, file_name=date_str + '.txt')
        # 翌月の日付を作成
        current_date += relativedelta(months=1)


def read_txt_file(file_name: str) -> float:
    """テキストファイルを解析し月積算下向き赤外放射量を取得する

    Args:
        file_name (str): 解析するファイル名

    Returns:
        float: 月積算下向き赤外放射量[MJ/m2]
    """

    # スキップする行を検索
    with open('out/' + file_name, encoding='utf8', newline='') as f:
        buffer = f.read()

    row_data = buffer.split('\n')
    for line_data in row_data:
        col_data = re.split(' +', line_data)
        if len(col_data) > 5 and col_data[1] == 'TOTAL':
            if col_data[26] != 'XXXX':
                return float(col_data[26]) * 0.01
            else:
                return -999.0


def total_downward_radiation():
    """指定する期間の上向き赤外放射量の月積算値を取得する
    """

    ds = datetime.date(1993, 1, 1)
    de = datetime.date(2023, 4, 1)

    # 開始日から終了日まで月ごとにループ
    current_date = ds
    i = 0
    columns = ['date', 'DOWNWARD_LONGWAVE_RADIATION']
    df_longwave_rad = pd.DataFrame(columns=columns)
    while current_date <= de:
        print(current_date.strftime("%Y-%m"))

        # ダウンロードして保存済みのテキストファイル名作成
        file_name = str(current_date.year).zfill(4) + str(current_date.month).zfill(2) + '.txt'

        df_longwave_rad.loc[i, 'date'] = current_date
        df_longwave_rad.loc[i, 'DOWNWARD_LONGWAVE_RADIATION'] = read_txt_file(file_name=file_name)
        i += 1
        current_date += relativedelta(months=1)

    # 結果をCSVファイルに保存する
    df_longwave_rad.to_csv('result.csv')


def str2float(weather_data: str) -> float:
    """文字列を数値に変換

    Args:
        weather_data (str): 変換元の文字列

    Returns:
        float: 数値データ
    """
    try:
        return float(weather_data)
    except:
        return 0
    

def scraping(url: str, date: datetime):
    """気象庁の毎時気象データ閲覧ページを解析し日気象データを作成する
        以下サイトを参考にした
        https://www.gis-py.com/entry/scraping-weather-data

    Args:
        url (str): 気象庁のページURL
        date (datetime): 対象とする日付

    Returns:
        _type_: 気象データで構成される2次元配列を返す
    """

    # 気象データのページを取得
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)
    trs = soup.find("table", { "class" : "data2_s" })

    data_list = []
    data_list_per_hour = []

    # table の中身を取得
    for tr in trs.findAll('tr')[2:]:
        tds = tr.findAll('td')

        if tds[1].string == None:
            break;

        data_list.append(date)
        data_list.append(tds[0].string)
        data_list.append(str2float(tds[1].string))
        data_list.append(str2float(tds[2].string))
        data_list.append(str2float(tds[3].string))
        data_list.append(str2float(tds[4].string))
        data_list.append(str2float(tds[5].string))
        data_list.append(str2float(tds[6].string))
        data_list.append(str2float(tds[7].string))
        data_list.append(str2float(tds[8].string))
        data_list.append(str2float(tds[9].string))
        data_list.append(str2float(tds[10].string))
        data_list.append(str2float(tds[11].string))
        data_list.append(str2float(tds[12].string))
        data_list.append(str2float(tds[13].string))

        data_list_per_hour.append(data_list)

        data_list = []

    return data_list_per_hour


def get_weather_data():
    """気象庁サーバから指定期間の気象データをダウンロードする
    """

    ds = datetime.date(1993, 1, 1)
    de = datetime.date(2023, 4, 30)
    # de = datetime.date(1993, 1, 2)

    # CSV の列
    fields = ["年月日", "時間", "気圧（現地）", "気圧（海面）",
              "降水量", "気温", "露点湿度", "蒸気圧", "湿度",
              "風速", "風向", "日照時間", "全天日射量", "降雪", "積雪"] # 天気、雲量、視程は今回は対象外とする

    with open('weather/tateno_weather_data.csv', 'w', encoding='shiftJIS') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(fields)
        for i in range((de - ds).days + 1):
            # time.sleep(15)
            date = ds + datetime.timedelta(i)

            print(date)

            # 対象url（今回は館野）
            url = "http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php?" \
                    "prec_no=40&block_no=47646&year=%d&month=%d&day=%d&view="%(date.year, date.month, date.day)

            data_per_day = scraping(url, date)
            for dpd in data_per_day:
                    writer.writerow(dpd)


def calc_R_GRD():
    """上向き長波長放射量を計算する（地表面温度は外気温度相当と仮定）
    """
    
    # ステファンボルツマン定数
    sgm = 5.67e-8
    pd_weather = pd.read_csv('weather/tateno_weather_data.csv', encoding='shift-JIS', parse_dates=['年月日'])
    pd_weather.set_index('年月日', inplace=True)
    pd_weather['R_GRD'] = sgm * (pd_weather['気温'] + 273.15) ** 4
    pd_monthly = pd_weather.resample('M').sum()
    pd_monthly = pd_monthly.drop([
        '時間',
        '気圧（現地）',
        '気圧（海面）',
        '降水量',
        '気温',
        '露点温度',
        '蒸気圧',
        '湿度',
        '風速',
        '風向',
        '日照時間',
        '降雪',
        '積雪'
        ], axis=1)
    pd_monthly['R_GRD'] = pd_monthly['R_GRD'] * 3600.0 / 1.0e6

    pd_monthly.to_csv('weather/upward_radiation.csv', encoding='utf-8')


if __name__ == '__main__':

    download_downward_radiation()
    total_downward_radiation()
    get_weather_data()
    calc_R_GRD()
