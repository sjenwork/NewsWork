import pandas as pd
from conn_sql import connectDB
import datetime
import re, sys
import shutil
import subprocess

pd.options.mode.chained_assignment=None
pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)


def makesql():
    sql = f'''  select * from [ChemiBigData].[dbo].[Raw_news]
                where update_time between '{UPDATE_TIME}' and '{UPDATE_TIME} 23:59' 
                and website in ('NYTimes', 'European_Commission', 'US_fda', '香港-食物安全中心', '加拿大食物檢驗局'
                                ,'愛爾蘭食品安全局', '歐洲食品安全管理局', '美國食品安全新聞', '英國食品標準管理局', 
                                '澳門特別行政區政府食品安全資訊', '澳洲紐西蘭食物標準')                             
                or website like '%Journal%' '''
    return re.sub('[\n|\s]{1,}',' ', sql)

def preproc(data):
    data = data.drop_duplicates(subset='news_content')
    data.update_time =  datetime.datetime.now()
    return data

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        UPDATE_TIME = sys.argv[1]
        print(f'  >> Condition 1: 讀取到使用者輸入的「日期」：{UPDATE_TIME}')
    elif len(sys.argv) > 0:
        UPDATE_TIME = datetime.datetime.today().strftime('%Y-%m-%d')
        print(f'  >> Condition 2: 處理日期：{UPDATE_TIME}')


    
    print(f' 0. 讀取資料庫資料')
    c    = connectDB()
    data = c.fetch(makesql())

    print(f'   >>> 0.1 資料前處理')
    data = preproc(data)

    print(f'   >>> 0.2 讀取到{len(data)}筆新聞資料，將資料寫入待預測資料 "DATA/pred_set.xlsx"')
    data.to_excel(f'DATA/pred_set_aboard.xlsx', index=False)
   
    print(f' 1. 尋找新聞內出現之化學物質')
    exec(open('./6.findChemistry_aboard.py').read())
    
    print(f' 2. 開始預測新聞分類')
    exec(open('./7.NewsClassify_aboard.py').read())
    
    print(f'   >>> 2.1 將新聞預測結果存入每日之新聞資料')
    shutil.copyfile('DATA/Result_aboard_merged.xlsx', f'daily_news_aboard/{UPDATE_TIME}.xlsx')
    
    print(f' 3. 將預測分類與化學物質表整理成網頁系統需要之格式')
    subprocess.run(f'/work/miniconda3/envs/work/bin/python 8.postProc_aboard.py {UPDATE_TIME}', shell=True)
