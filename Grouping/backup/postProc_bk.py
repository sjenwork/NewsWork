import pandas as pd
from conn_sql import connectDB
import datetime
import re
import shutil
import numpy as np
import sys

pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)

time = sys.argv[1]
print(f'輸入日期為 {time}')
#time = datetime.datetime.today().strftime('%Y-%m-%d')
#time = '2020-09-26'

fileName = f'daily_news/{time}.xlsx'

news_cols = ['其他', '毒品', '災害防治', '無關', '環境汙染', '食品安全']
use_cols = ['id', 'keyword', 'title', 'website', 'update_time', 
            'publish_date', 'publish_time', 'web_url', 'news_content', 'Chemical_material' ] + news_cols

df = pd.read_excel(fileName, index_col=0)
for col in use_cols:
    if col not in df.columns:
        df[col] = 0
df = df[use_cols]
df['res'] = None

'''
<=============  處理新聞預測結果 ================>
'''
ind = list(df.columns).index('Chemical_material') + 1
res = df.iloc[:,ind:]
res['res'] = None
res['res'] = res.drop('無關',axis=1).sum(axis=1)
res.loc[res['res']<0.1,'res'] = '無關'
df.res.loc[res.res=='無關'] = '無關'
res =  res[res.res!='無關'].drop('無關', axis=1)
news_cols2 = [i for i in news_cols if i !='無關']
res['res'] = res.iloc[:,:-1].apply(lambda i: news_cols2[np.argmax(i)], axis=1)
df.loc[res.res.index,'res'] =  res.res

dfres = df[['id','res']]
dfres = dfres.rename({'res':'label'}, axis=1)
dfres['lang'] = 0
dfres = dfres[dfres['label']!='無關']

lname = { '食品安全': 'food','環境汙染': 'env' ,'毒品': 'drug' ,'災害防治': 'disaster' ,'其他': 'other' } 
dfres = dfres.replace(lname)


c = connectDB()
c.push(dfres, '[ChemiBigData].[dbo].[新聞分群_國內新聞_結果]')

'''
<============= 處理包含化學物質 ================>
'''
if 1 == 1:
    df = df[df.res!='無關']
    df = df.drop(news_cols + ['res'], axis=1)
    df = df.dropna(subset=['Chemical_material'])


    chem = pd.DataFrame(df['Chemical_material'].str.split('、').to_list(), index=df.index)
    chem.columns = [f'chem_{i}' for i in range(len(chem.columns))]
    chem.index.name = 'index'
    chem = chem.reset_index()
    chem = pd.wide_to_long(chem, ['chem_'], i='index', j='count').dropna()
    chem = chem.droplevel(1, axis=0)
    chem.columns = ['ChemicalChnName']
    df = df.merge(chem, how='right', left_on=df.index, right_on=chem.index)
    df = df.drop(['key_0', 'Chemical_material'], axis=1)



    ref_flatten = pd.read_csv('ReadData/Guidelines2_revised_flattenName.csv', index_col=0).fillna('').set_index('name_all')['MatchNo']
    ref_flatten = ref_flatten.to_dict()
    df['MatchNo'] = df.ChemicalChnName.map(ref_flatten)

    ref = pd.read_csv('ReadData/Guidelines2.csv', index_col=0).fillna('')[['CASNoMatch', 'ChemiChnNameMatch', 'ChemiEngNameMatch']]
    ref2casno = ref['CASNoMatch'].to_dict()
    ref2ename = ref['ChemiEngNameMatch'].to_dict()
    df['CASNo'] = df.MatchNo.map(ref2casno)
    df['chemiTarget'] = df.MatchNo.map(ref2ename)
    df = df.drop('MatchNo', axis=1)
    df['in_chemistry_list'] = 1
    df=df.rename({'update_time':'updatetime'}, axis=1)


    c = connectDB()
    c.push(df, '[ChemiBigData].[dbo].[網路擷取分析_國內proc1_新聞對應化學物質]')


df3 = pd.DataFrame()
df3['id'] = df.id
df3['status'] = '正常'
df3['push_status'] = '正常'
#df3['pushed_date'] = ''

c = connectDB()
c.push(df3, '[ChemiBigData].[dbo].[新聞分群_國內新聞_狀態]')

