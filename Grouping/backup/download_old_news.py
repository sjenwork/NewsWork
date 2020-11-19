import pandas as pd
from conn_sql import connectDB
import datetime
import datetime

data = pd.read_excel('../revising/update_2020-10-07.xlsx')
c = connectDB()

if 1==1:
    #data = data.rename({'updatetime':'update_time'}, axis=1)
    data.drop_duplicates(subset=['title','news_content'])
    data['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for i in range(100):
        i0 = 1000*i
        i1 = 1000*(i+1)
        if i0>len(data):
            continue
        tmp = data.iloc[i0:i1]
        print(i)
        c.push(tmp, '[ChemiBigData].[dbo].[Raw_news]')
