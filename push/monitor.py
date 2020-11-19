import pandas as pd
from push import push
from conn_sql import connectDB
from pathlib import Path
import os, datetime, re


def processTimeoffset(time):
    import struct, dateutil

    m = list(struct.unpack('QIhH', time))

    days= m[1]
    microseconds = m[0] /10 if m[0] else 0
    timezone = m[2]
    tz = dateutil.tz.tzoffset('ANY',timezone * 60  )
    my_date = datetime.datetime(*[1900,1,1,0,0,0], tzinfo=tz)
    td = datetime.timedelta(days=days,minutes=m[2],microseconds=microseconds)
    my_date += td
    return my_date

class monitor():
    def __init__(self, time=None):
        if time is None:
            time = datetime.datetime.now().strftime('%Y-%m-%d')
        self.time = time
        #time = pd.to_datetime(time)
        self.conn = connectDB()
        self.update(time)
       
    def getcont(self, path):
        with open(path, encoding='big5') as f:
            lines = f.readlines()
        cont = [] 
        for line in lines:
            line = line.replace("'", '"')
            cont.append(f'<p>{line.strip()}</p>')
        return ' '.join(cont)


    def createsql(self, action):
        getsql = f''' select * from [ChemiBigData].[dbo].[loginfo]
                  where Date = '{self.time}'
        '''
        getsql = ' '.join(getsql.split()) 

        now = datetime.datetime.now()        
        #title = getTitle()
        #content = getCont()
        title = ''
        content = ''
        insertsql = f'''insert [ChemiBigData].[dbo].[loginfo]
                    (Date, title, content, updatetime)
                    Values('{self.time}', 'TITLE', 'CONTENT', '{now.strftime("%Y-%m-%d %H:%M:%S")}')
        '''
        insertsql = ' '.join(insertsql.split())
        resp = {'get': getsql,
                'insert': insertsql}
        return resp[action]

    def proctime(self, res):
        for i,j in res.iterrows():
            res.loc[i, 'updatetime'] = processTimeoffset(j['updatetime'])
        return res

    def update(self, time):
        path = Path(os.path.abspath('../Crawler/DATA/log'))
        logs = [os.path.join(path, i) for i in os.listdir(os.path.join(path)) if re.match(f'.*{time}.*err', i)]
        status = {i: os.stat(i).st_size for i in logs}

        sql = self.createsql(action='get')
        res = self.conn.fetch(sql)
        res = self.proctime(res)
        #return
        for i in status.items():
            title = i[0].split('/')[-1]
            size = i[1]
            #if True:
            if title not in list(res['title']) and size!=0:
                #if title != 'getNews_2020-10-13_美國食藥局.err': continue
                print(f'get mew {title}, updating database')

                pushedcont = self.getcont(i[0])#.encode('Big5')
                sql = self.createsql(action='insert')
                sql = (sql.replace('TITLE', title)
                          .replace('CONTENT', pushedcont)  
                        )
                #print(sql)
                self.conn.cursor.execute(sql)
                self.conn.cnxn.commit()

                para = {'target' : 'jen',
                        'Title'  : '爬蟲記錄檔錯誤訊息推播',
                        'Content': '爬蟲錯誤訊息，詳見附加檔案',
                        'PushFile': pushedcont,
                        'FileName': f'{title.replace("err","html")}'
                }
                push(**para)
                self.para = para

        self.sql = sql
        self.res = res
        self.status = status


if __name__ == '__main__':
    para = {'time': '2020-10-13',
            }

    m = monitor(**para)
