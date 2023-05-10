import openpyxl
import xlwings as xw

'''
ワークシート関数を有するエクセルファイルをPythonで操作します。
PythonからA1セルに値を入力し、B1セル（'=A1*2' が入力済み）の値を取得します。
エクセルは、保存のタイミングでファイルに値を保存するので、
xlwingsを利用します。（つまり、実行環境にエクセルが入っている必要があります）

値を取得するのは高速なopenpyxlを利用します。
'''

# Excelが画面に表示されないようにする
xw.App(visible=False)

# Excelファイルを開く
wb = xw.Book('test.xlsx')
sheet = wb.sheets['Sheet1']
# A1セルに3を入力する
sheet.range('A1').value = 3
# 保存する
wb.save('test.xlsx')
# 閉じる
wb.close()

wb = openpyxl.load_workbook('test.xlsx', data_only=True)
sheet = wb['Sheet1']
print(sheet['B1'].value)
