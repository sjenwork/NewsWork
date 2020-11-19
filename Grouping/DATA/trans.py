#!/Users/jen/miniconda3/envs/work/bin/python
import pandas as pd

df = pd.read_excel('Result_merged.xlsx', index_col=0)
e2c = {'env':'環境汙染', 'disaster': '災害防治', 'food': '食品安全', 'other': '其他', 'drug': '毒品'}

df = df.drop_duplicates(subset='news_content').replace(e2c)

res = df.iloc[:, -6:]
tmp=[]
for i,j in res.iterrows():
    if i>1000:
        continue
    if j.drop('無關').sum() > 0.3:
        j['無關'] = 0
    tmp.append(j.to_frame().T)
res = pd.concat(tmp)

pred = res.apply(lambda i: res.columns[i.argmax()], axis=1)
df['pred'] = pred
df = df.reset_index(drop=True)
df.to_excel('test.xlsx')
