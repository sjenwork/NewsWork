import os, sys, re, platform
import pandas as pd
import numpy as np
import datetime
import sys


class getRef():
    def __init__(self):
        super(getRef, self).__init__()
        self._getRegexTable()
        self._getStopWord()
        self._getIndexTable()

    def _getStopWord(self): 
        with open('ReadData/stopWords.txt', 'r', encoding='utf-8') as f:
            df = f.readlines()
        df = '|'.join([re.sub('\n|\s+','', i) for i in df])
        df = re.sub('\ufeff', '', df)
        df = df.replace('?', '\?')
        df = df.replace('.', '\.')
        df = df.replace('（', '\（')
        df = df.replace('）', '\）')
        df = df.replace('(', '\(')
        df = df.replace(')', '\)')
        self.stopwords = df

    def _getRegexTable(self):
        with open('ReadData/KeywordPos.txt', 'r', encoding='utf-8') as f:
        #with open(self.pathRegexTab, 'r') as f:
            dfpos = f.readlines()
        dfpos = ' '.join(dfpos)
        dfpos = re.sub('\n+|\s+',' ', dfpos)
        dfpos = re.split('\s+', dfpos)
        dfpos = [i for i in dfpos if i!='']
        dfpos = [i for i in dfpos if i[0] !='#']
        self.Regex = '|'.join(dfpos)

    def _getIndexTable(self):
        print('  >> 讀取指引表')
        df = pd.read_excel('ReadData/指引表.xlsx', index_col=0)
        #df = pd.read_excel(self.indexTable, index_col=0)
        df.columns = ['CasNo', 'Cname', 'Ename', 'Cname2', 'Ename2']
        df.index.name = 'MatchNo'
        self.index = df

        print('  >> 定義中文名稱對照表')
        self.Cname  = self._procName(df, 'Cname' , plus='|汞|砷|氰酸鉀')
        print('  >> 定義中文其他名稱對照表')
        self.Cname2 = self._procName(df, 'Cname2', minus='SA\|')

    def _procName(self, df, colName, plus='', minus=''):
        name = df[colName]
        if colName == 'Cname':
            name = pd.Series(re.sub('\s+', '', ';'.join(name.dropna())).split(';'))
        name = re.sub('\s+', '',  '|'.join(name[(name.str.len()<10) & (name.str.len()>1)]))
        name = name.replace('?', '\?')
        name = name.replace('.', '\.')
        name = name.replace('（', '\（')
        name = name.replace('）', '\）')
        name = name.replace('(', '\(')
        name = name.replace(')', '\)')
        name = name.replace('+', '\+')
        name+= plus
        name = re.sub(minus, '', name)
        return name


class findChem(getRef):
    def __init__(self):
        super(findChem, self).__init__()

        self.dfraw = self._readData()
        self.df_withChem = self._confirmChem(self.dfraw)
        self.df_findChem = self._findChem(self.df_withChem)

    def _readData(self):
        df = pd.read_excel('DATA/pred_set.xlsx', index_col=0)
        return df

    def _confirmChem(self, df):
        content = df['news_content']
        df_withChem = content.str.contains(self.Regex)
        df_withChem = df[df_withChem]
        return df_withChem

    def _findChem(self, df):
        content = df['news_content']
        print('  >>> 尋找中文名稱關鍵字')
        res1 = content.str.findall(self.Cname)
        print('  >>> 尋找中文別名關鍵字')
        res2 = content.str.findall(self.Cname2)
        self.content = content
        res = (res1 + res2).apply(lambda i: '、'.join(np.unique(i)))
        res.name = 'Chemical_material'
        df = df.join(res)
        df = pd.concat([self.dfraw, df], axis=0).reset_index().drop_duplicates(subset='id', keep='last')
        self.df = df
        df.to_excel('DATA/pred_set.xlsx')
        return df
        

if __name__ == '__main__':
    f = findChem()
