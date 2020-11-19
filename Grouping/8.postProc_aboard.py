import pandas as pd
from conn_sql import connectDB
import datetime
import re
import shutil
import numpy as np
import sys

pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)

class header():
    def __init__(self):
        labels   = ['其他', '毒品', '災害防治', '無關', '環境汙染', '食品安全']
        labels2  = ['其他', '毒品', '災害防治', '環境汙染', '食品安全']
        headers  = ['id', 'keyword', 'title', 'website', 'update_time', 'publish_date', 'publish_time', 'web_url', 'news_content', 'Chemical_material' ] + labels
        headers2 = ['id', 'keyword', 'title', 'website', 'update_time', 'publish_date', 'publish_time', 'web_url', 'news_content', 'Chemical_material' ]
        self.labels = labels
        self.labels2 = labels2
        self.headers = headers
        self.headers2 = headers2

class preproc(header):
    def __init__(self, time):
        super(preproc, self).__init__()

    def run(self):
        df = self.__formatting__()
        df = self.__result__(df)
        return df

    def __formatting__(self):
        fileName = f'daily_news_aboard/{time}.xlsx'
        df = pd.read_excel(fileName, index_col=0)
        for col in self.labels:
            if col not in df.columns:
                df[col] = 0
        df = df[self.headers]
        df['pred_label'] = None
        
        self.fileName = fileName
        return df

    def __result__(self, df):
        res = df.loc[:, '其他': 'pred_label']
        ind = res[res['無關']>0.3].index
        df.loc[ind, 'pred_label'] = '無關'
        res = res.drop(index=ind).drop('無關', axis=1)
        res['pred_label'] = res.loc[:, self.labels2].apply(lambda i: self.labels2[np.argmax(i)], axis=1)
        df.loc[res['pred_label'].index, 'pred_label'] =  res['pred_label']
        df.to_excel(self.fileName)     
  
        self.df = df 
        return df 

def newsRes(df):
    dfres = df[['id', 'pred_label']].rename({'pred_label': 'label'}, axis=1)
    dfres['lang'] = 1
    dfres = dfres[dfres['label']!='無關']
    
    lname = { '食品安全': 'food','環境汙染': 'env' ,'毒品': 'drug' ,'災害防治': 'disaster' ,'其他': 'other' } 
    dfres = dfres.replace(lname)
    return dfres


class ref():
    def __init__(self):
        self.chem2matchno = self.__ch2m__()
        self.chem2casno, self.chem2ename, self.chem2cname  = self.__getName__()

    def __ch2m__(self): 
        chem2matchno = pd.read_csv('ReadData/Guidelines2_revised_flattenName.csv', index_col=0).fillna('').set_index('name_all')['MatchNo']
        chem2matchno = chem2matchno.to_dict()
        return chem2matchno

    def __getName__(self):
        ref = pd.read_csv('ReadData/Guidelines2.csv', index_col=0).fillna('')[['CASNoMatch', 'ChemiChnNameMatch', 'ChemiEngNameMatch']]
        ref2casno = ref['CASNoMatch'].to_dict()
        ref2ename = ref['ChemiEngNameMatch'].to_dict()
        ref2cname = ref['ChemiChnNameMatch'].to_dict()
        return ref2casno, ref2ename, ref2cname

class matchChem(header, ref):
    def __init__(self):
        super(matchChem, self).__init__()
        super(header   , self).__init__()

    def run(self, df):
        df = self.__select__(df)
        df = self.__proc__(df)
        df = self.__match__(df)
        self.df = df
        return df

    def __select__(self, df) :
        df = df[df['pred_label']!='無關']
        df = df.loc[:, self.headers2]
        df = df.dropna(subset=['Chemical_material'])
        return df
   
    def __proc__(self, df) :
        chem = pd.DataFrame(df['Chemical_material'].str.split('、').to_list(), index=df.index)
        chem.columns = [f'chem_{i}' for i in range(len(chem.columns))]
        chem.index.name = 'index'
        chem = chem.reset_index()
        chem = pd.wide_to_long(chem, ['chem_'], i='index', j='count').dropna()
        chem = chem.droplevel(1, axis=0)
        chem.columns = ['ChemiEngName']

        df = df.merge(chem, how='right', left_on=df.index, right_on=chem.index)
        df = df.drop(['key_0', 'Chemical_material'], axis=1)
        return df
    
    def __match__(self, df):
        df['MatchNo']       = df.ChemiEngName.map(self.chem2matchno)
        df['CASNo']         = df.MatchNo.map(self.chem2casno)
        df['chemiTarget']   = df.MatchNo.map(self.chem2ename)
        df['ChemiChnName']  = df.MatchNo.map(self.chem2cname)
        df = df.drop('MatchNo', axis=1)
        df['in_chemistry_list'] = 1
        df = df.rename({'update_time':'updatetime'}, axis=1)
        return df
    
def status(df):
    df2 = pd.DataFrame()
    df2['id'] = df.id
    df2['status'] = '正常'
    df2['push_status'] = '正常'
    return df2

if __name__ == '__main__':
    time = sys.argv[1]
    print(f'   >>> 3.1 輸入日期為 {time}')

    print(f'   >>> 3.2 決定分類結果')
    df = preproc(time).run()


    print(f'   >>> 3.3 新聞分群_國內新聞_結果')        
    df_label = newsRes(df)

    print(f'   >>> 3.4 網路擷取分析_國外proc1_新聞英文對應化學物質') 
    df_proc = matchChem().run(df)
    
    print(f'   >>> 3.5 新聞分群_國內新聞_狀態') 
    df_status = status(df) 

    #
    print(f'   >>> 3.6 更新資料庫') 
    c = connectDB()
    c.push(df_label , '[ChemiBigData].[dbo].[新聞分群_國內新聞_結果]')
    c.push(df_proc  , '[ChemiBigData].[dbo].[網路擷取分析_國外proc1_新聞英文對應化學物質]')
    c.push(df_status, '[ChemiBigData].[dbo].[新聞分群_國內新聞_狀態]')

