import pandas as pd
import numpy as np
import re

#df = pd.read_csv('ReadData/Guidelines2.csv', index_col=0)
#df = df.fillna('')
#df = df.astype(str)
#df.columns = ['CasNo', 'Cname', 'Ename', 'Cname2', 'Ename2']
#
#ename = df['Ename'] + ';' + df['Ename2']
#ename = ename.str.replace('\s+', ' ')
#ename = ename.str.replace('\s{0,};+\s{0,}', ';')
#ename = ename.str.replace(';$', '')
#ename = ename.str.replace('^;', '')
#ename = ename.str.replace('\u200b', '')
#ename = ename.str.replace('^-$', '')
#ename = ename.str.replace('0.0', '')
#ename.name = 'ename'
#ename.index = df.index
#ename = ename.to_frame()
#ename = ename.reset_index()
#ename = ename.reset_index()
#
#data = ename['ename'].str.split(';').to_list()
#num = np.max([len(i) for i in data])
#data_cut = pd.DataFrame(data, columns=[f'ename{i}' for i in range(num)])
#ename = ename.drop('ename', axis=1)
#ename = pd.concat([ename, data_cut], axis=1)
#ename = pd.wide_to_long(ename, [f'ename'], i='index', j='nameCnt')
#ename = ename.dropna(subset=[f'ename'])
#ename.index = ename.index.droplevel(1)
#ename = ename.sort_index()
#ename.index = range(len(ename))
#
#ename.ename = ename.ename.str.replace('^\s{1,}$','')
#ename = ename[ename.ename!='']
#
#ename.to_csv('')

drop_kw = 'bit;ups;Confirm;etc;dexamethasone;Demand;ICE;Co;Ito;Freedom;His;prowl;3-;eco;Task;Pops;ASPIRIN;alpha;freedom;affinity;his;Va;Ruby;confirm;tag;her;St;met;defend;starch;gala;HBO;retain;crown;him;be;reason;an;tan;age;task;faster;A14;Atlas;blazer;pp;bloc;map;Oct;DDS;alert;bent;Can;trial;white;Al;up;camp;triumph;dead;tips;e-;runner;orbit;em;assert;pan;da;Mark A;glean;bullet;goal;score;oil;debut;a T;Dec;punch;Red;tape;gun;most;;ask;tee;White;pops;ad;ha;no;focus;dividend;Sonata;est;saga;banner;An;Ailes;formal;balance;As;a co;damn;ace;carbon;des;rapid;ever;San;summit;vanguard;TNT;add;lead;ardent;CBS;partner;dim;can;mobs;per;equal;as;Bon;avid;blue;demand;germane;memo;giant;Sudan;water;has;made;missile;No;Predict'


drop_kw = drop_kw.lower().split(';')

#df_raw = pd.read_csv('ReadData/Guidelines2.csv', index_col=0)
df = pd.read_csv('ReadData/Guideline_ename.csv', index_col=0)
df = df.drop_duplicates(subset='ename')
df = df[df.ename.str.len()>4]
df = df[df.ename.str.len()<20]
df = df[~df.ename.str.lower().isin(drop_kw)]


df.ename = df.ename.str.replace('\\', ' ')
df.ename = df.ename.apply(lambda i: f'\\b{i}\\b')
matchstr = '|'.join(df['ename'])
matchstr = matchstr.replace('+', '\+') 
matchstr = matchstr.replace('?', '\?') 
matchstr = matchstr.replace('.', '\.') 
matchstr = matchstr.replace('*', '\*') 
matchstr = matchstr.replace('(', '\(') 
matchstr = matchstr.replace(')', '\)') 
matchstr = matchstr.replace('[', '\[') 
matchstr = matchstr.replace('}', '\}') 
matchstr = matchstr.replace('{', '\{') 
matchstr = matchstr.replace(']', '\]') 

news = pd.read_excel('DATA/pred_set_aboard.xlsx')
if 'Unnamed: 0' in news.columns:
    news = news.drop('Unnamed: 0', axis=1)
content = news['news_content'].fillna('')
res = content.apply(lambda i: re.findall(matchstr, i, re.IGNORECASE))
res = res.apply(lambda i: '、'.join(set([j.lower() for j in i])))
res.name = 'Chemical_material'
news = pd.concat([news, res], axis=1)
news.to_excel('DATA/pred_set_aboard.xlsx', index=False)
