import pandas as pd
import glob
import datetime
from conn_sql import connectDB

allfile = glob.glob('test_data/*')


colmap= {'關鍵字': 'keyword', 
        '標題': 'title', 
        '網站': 'website', 
        '發布日期時間': 'publish_time', 
        '網址': 'web_url', 
        '內文': 'news_content',
        }

for i in allfile[:]:
    df = pd.read_excel(i, index_col=0)
    #df = df.rename(colmap, axis=1)
    #df['publish_date'] = df.publish_time.dt.strftime('%Y-%m-%d')
    #df['update_time'] = datetime.datetime.now()
    #df.to_excel(i)
    c = connectDB()
    c.push(df, '[ChemiBigData].[dbo].[Raw_news]')
