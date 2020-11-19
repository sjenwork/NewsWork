import pandas as pd
from conn_sql import connectDB
import datetime, os
pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)

class wrtie2db(connectDB):
    def __init__(self, time=None):
        if time is None:
            time = datetime.datetime.today()
        self.data = self.__merge__(time)
        self.todb(self.data, time)


    def __merge__(self, time): 
        JournalList = [ 'Environmental_Pollution', 'Environmental_Research', 'Environment_International', 'Science_of_the_total_environment', 'Journal_of_Food_and_Drug_Analysis' ]
        pth = 'DATA/Journal/'
        data = []
        for inews in JournalList:
            fullpath = os.path.join(pth, inews, f'{time.strftime("%Y-%m-%d")}.xls')
            if os.path.isfile(fullpath):
                tmp = pd.read_excel(fullpath)
                print(f'找到: {fullpath}，共 {len(tmp)} 筆資料')
                data.append(tmp)
        data = pd.concat(data).drop_duplicates(subset='title').dropna(subset=['news_content'])
        if len(data) == 0 :
            return None
        #data = data[~data.title.str.match('^[a-zA-Z]+$')]
        data = data.sort_values(by='Keyword').reset_index(drop=True)
        
        data['title'] = data['title'].apply(lambda i:i[:120])
        data['update_time'] = datetime.datetime.now() 
           
        data = data.drop(['Authors'], axis=1) 
        return data

    def todb(self, data, time):
        super(wrtie2db, self).__init__()
        predate = (time + datetime.timedelta(days=-5)).strftime('%Y-%m-%d')
        code = f'''select title from [ChemiBigData].[dbo].[Raw_news]  where update_time>'{predate}' and website like '%Journal%' '''
        olddata = self.fetch(code).drop_duplicates().dropna()
        length0 = len(data)
        data = data.set_index('title').drop(olddata.title).reset_index(drop=False)
        length1 = len(data)
        print(f'>> 比對已擷取資料，並移除重複數據{length0-length1}筆')
        if data is not None and not data.empty:
            self.push(data, '[ChemiBigData].[dbo].[Raw_news]')
        else:
            print('>> 沒有可更新的內容')

        self.olddata = olddata
        self.data = data

       

if __name__ == '__main__':
    time = '2020-10-01'
    time = datetime.datetime.today().strftime('%Y-%m-%d')
    w = wrtie2db()
