import pandas as pd
from conn_sql import connectDB
import datetime, re


class push:
    def __init__(self, target, PushDate=None ,Title='測試推播' ,Content='無內文' ,PushFile='NULL' ,FileName='NULL'):
        now = datetime.datetime.now()
        if PushDate is None:
            PushDate = now.strftime('%Y/%m/%d')
        Object = f'、{target}、'
        CreateAccount = target
        PT_no = f'{PushDate} {Title} {now.strftime("%H%M%S")}'
        CreateDate = now.strftime('%Y/%m/%d %H:%M:%S')
        Title = f'{Title}[{now.strftime("%Y/%m/%d")}]'

        self.conn = connectDB()
        self.Notification(PushDate, Title, Content, PushFile, FileName, Object, CreateAccount, PT_no, CreateDate)
        self.NotificationUnread(PushDate, Title, CreateAccount, PT_no, CreateDate)

    def Notification(self, PushDate, Title, Content, PushFile, FileName, Object, CreateAccount, PT_no, CreateDate): 

        sql = ''' insert [ChemiPrimary].[dbo].[Notification] 
                ( [PushDate] ,
                  [Title] ,
                  [Content] ,
                  [PushFile] ,
                  [FileName] ,
                  [Object] ,
                  [CreateAccount] ,
                  [PT_no] ,  
                  [CreateDate])
                Values('PUSHDATE', 'TITLE', 'CONTENT', CONVERT(VARBINARY(MAX), CAST('PUSHFILE' AS VARBINARY(MAX)), 1), 'FILENAME', 'OBJECT', 'ACCOUNT', 'PT_NO', 'CREATEDATE') '''


        sql = (sql.replace('PUSHDATE'     ,  PushDate     )
                  .replace('TITLE'        ,  Title        )
                  .replace('CONTENT'      ,  Content      )
                  .replace('PUSHFILE'     ,  PushFile     )
                  .replace('FILENAME'     ,  FileName     )
                  .replace('OBJECT'       ,  Object       )
                  .replace('ACCOUNT'      ,  CreateAccount)
                  .replace('PT_NO'        ,  PT_no        )
                  .replace('CREATEDATE'   ,  CreateDate   ))

        sql = re.sub("'NULL'", 'NULL', sql) 
        sql = ' '.join(sql.split()) 
        print(sql)
        self.conn.cursor.execute(sql)
        self.conn.cnxn.commit()

    def NotificationUnread(self, PushDate, Title, Object, PT_no, CreateDate): 

        sql = ''' insert [ChemiPrimary].[dbo].[NotificationUnread] 
                  ([PushDate],
                   [Title],
                   [Object],
                   [PT_no],
                   [CreateDate])
                Values('PUSHDATE', 'TITLE', 'OBJECT', 'PT_NO', 'CREATEDATE') '''

        sql = (sql.replace('PUSHDATE'     ,  PushDate     )
                  .replace('TITLE'        ,  Title        )
                  .replace('OBJECT'       ,  Object       )
                  .replace('PT_NO'        ,  PT_no        )
                  .replace('CREATEDATE'   ,  CreateDate   ))

        sql = re.sub("'NULL'", 'NULL', sql) 
        sql = ' '.join(sql.split()) 
        print(sql)
        self.conn.cursor.execute(sql)
        self.conn.cnxn.commit()

if __name__ == '__main__':
    content = lambda i: open('mail.html', 'r').readlines().split()

    para = {'target': 'jen',
            'Title' : '新聞爬蟲異常紀錄',
            'Content' : content
            }
    push(**para)

