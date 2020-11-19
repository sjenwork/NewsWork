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
        news_chn = ['自由時報電子報', '中國時報電子報', '農傳媒', '聯合新聞網', '蘋果日報', '中央通訊社', '東森新聞報', '食力']
        news_eng = ['LibertyTimesNet' , 'chinaTimes' , 'agriharvest' , 'udn' , 'AppleDaily' , 'CNA' , 'ETtoday' , 'foodNEXT']
        pth = 'DATA/outNews/'
        data = []
        for inews in news_eng:
            fullpath = os.path.join(pth, inews, f'{time}.xls')
            if os.path.isfile(fullpath):
                data.append(pd.read_excel(fullpath))
        data = pd.concat(data).drop_duplicates(subset='title').dropna(subset=['news_content'])
        data = data[~data.title.str.match('^[a-zA-Z]+$')]
        data = data.sort_values(by='keyword').reset_index(drop=True)
        
        data['publish_date'] = data['publish_time'].dt.strftime('%Y-%m-%d')
        data['update_time'] = datetime.datetime.now() 
            
        return data

    def todb(self, data):
        super(wrtie2db, self).__init__()
        self.push(data, '[ChemiBigData].[dbo].[Raw_news]')

        
       

if __name__ == '__main__':
    w = wrtie2db()
