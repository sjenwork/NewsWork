import pandas as pd
import os, sys, re
from pathlib import Path
from configparser import ConfigParser
import socket
import pymssql

class connectDB():
    def __init__(self):
        machine = socket.gethostname()
        self.connect(machine)

    def connect(self, machine):
        config = ConfigParser()
        config.read('conf.ini')
        info = { 'server'    : config[machine]['server']
                ,'user'      : config[machine]['username']
                ,'password'  : config[machine]['password']
                ,'port'      : config[machine]['port']
                                }

        self.cnxn = pymssql.connect(**info)
        self.cursor = self.cnxn.cursor()

    def fetch(self, command):
        df = pd.read_sql(command, self.cnxn)
        self.df = df
        return df

    def push(self, data, table):
        print('   >> 資料上傳中')
        for i in range(100):         
            i0 = 1000*i         
            i1 = 1000*(i+1)         
            if i0>len(data):             
                continue         
            tmp = data.iloc[i0:i1]         
            print(f'  step {i}')         
            self.push0(tmp, table)


    def push0(self, data, table):
        columns = f'''({','.join(data.columns)})'''
        data = self.proc_data(data)
        cmd = f''' insert into {table} {columns} VALUES {data} '''
        self.cmd = cmd
        self.cursor.execute(cmd)
        self.cnxn.commit()


    def proc_data(self, data):
        data = data.fillna('')
        data = data.astype(str).applymap(lambda i:i.replace("'", ''))
        data = data.applymap(lambda i: re.sub('\n+', '', i))
        data = data.applymap("'{}'".format)
        data = data.apply(lambda i: ','.join(i.astype(str)), axis=1).to_frame()
        data = data.applymap('({})'.format)
        data = data.apply(lambda i: ','.join(i))[0]
        return data
        

if __name__ == '__main__':
    #machine = socket.gethostname()
    #title = '《上下游》報導紅豆使用固殺草安全性評估的三大誤解／蔡韙任'
    #data = pd.DataFrame(['2020-09-25', '安全', title, '農傳媒', 20000000], index=['publish_date', 'keyword', 'title', 'website', 'id']).T
    #data = data.append(data)
    #table = '[ChemiBigData].[dbo].[測試]'

    c = connectDB()
    #c.push(data=data, table=table)
    #tmp = c.fetch(f'select top 10 * from {table} order by id desc')
