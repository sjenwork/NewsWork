import pandas as pd
from conn_sql import connectDB
import datetime, os
pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)

class wrtie2db(connectDB):
    def __init__(self, time=None):
        if time is None:
            time = datetime.datetime.today().strftime('%Y-%m-%d')
        self.data = self.__merge__(time)
        self.todb(self.data)


    def __merge__(self, time): 
        news = ['European_Commission', '愛爾蘭食品安全局', '澳洲紐西蘭食物標準', 'US_FDA', '美國食品安全新聞',
                 '英國食品標準管理局', '香港食物安全中心', '澳門特別行政區政府食品安全資訊', '加拿大食物檢驗局', '歐洲食品安全管理局']
        pth = 'DATA/outNews_aboard/'
        data = []
        for inews in news:
            fullpath = os.path.join(pth, inews, f'{time}.xls')
            if os.path.isfile(fullpath):
                tmp = pd.read_excel(fullpath)
                print(f'找到: {fullpath}，共 {len(tmp)} 筆資料')
                data.append(tmp)
        data = pd.concat(data).drop_duplicates(subset='title').dropna(subset=['news_content'])
        if len(data) == 0 :
            return None
        data = data[~data.title.str.match('^[a-zA-Z]+$')]
        data = data.sort_values(by='keyword').reset_index(drop=True)
        
        data['title'] = data['title'].apply(lambda i:i[:120])
        data['publish_date'] = data['publish_time'].dt.strftime('%Y-%m-%d')
        data['update_time'] = datetime.datetime.now() 
            
        return data

    def todb(self, data):
        super(wrtie2db, self).__init__()
        if data is not None:
            self.push(data, '[ChemiBigData].[dbo].[Raw_news]')

        
       

if __name__ == '__main__':
    time = '2020-10-01'
    w = wrtie2db()
