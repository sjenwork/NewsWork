import pandas as pd
from conn_sql import connectDB
import datetime
import re, sys
import shutil
import subprocess
pd.options.mode.chained_assignment=None


UPDATE_TIME = datetime.datetime.today().strftime('%Y-%m-%d')

if len(sys.argv) >1:
    UPDATE_TIME = sys.argv[1]

sql = f'''
    select * from [ChemiBigData].[dbo].[Raw_news]
    where update_time between '{UPDATE_TIME}' and '{UPDATE_TIME} 23:59'
'''

#sql = f'''
#    select * from [ChemiBigData].[dbo].[news_data]
#    where updatetime > '{UPDATE_TIME}'
#'''

sql = re.sub('[\n|\s]{1,}',' ', sql)

print(' >> 讀取資料庫資料')
c = connectDB()
data = [] # not necessary
data = c.fetch(sql)
data = data.drop_duplicates(subset='news_content')
data.update_time =  datetime.datetime.now()

print(f' >> 讀取到{len(data)}筆新聞資料，將資料寫入待預測資料 "DATA/pred_set.xlsx"')
data.to_excel(f'DATA/pred_set.xlsx', index=False)

print(f' >> 找化學物質')
exec(open('./1.findChemistry.py').read())

print(f' >> 開始預測新聞分類')
exec(open('./2.NewsClassify.py').read())

print(f' >> 將預測結果寫入')
shutil.copyfile('DATA/Result_merged.xlsx', f'daily_news/{UPDATE_TIME}.xlsx')


print(f' >> 後續整理')
subprocess.run(f'/work/miniconda3/envs/work/bin/python 3.postProc.py {UPDATE_TIME}', shell=True)
