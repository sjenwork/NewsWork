import pandas as pd


newsList = [ 'NYTimes', 'European_Commission', 'US_fda', '香港-食物安全中心', '加拿大食物檢驗局'
            ,'愛爾蘭食品安全局', '歐洲食品安全管理局', '美國食品安全新聞', '英國食品標準管理局',
            '澳門特別行政區政府食品安全資訊', '澳洲紐西蘭食物標準']

fn = 'DATA/pred_set_aboard.xlsx'
df = pd.read_excel(fn).fillna('')
for col in ['其他', '毒品', '災害防治', '無關', '環境汙染', '食品安全']:
    df[col] = 0
df.loc[df['website']!='NYTimes', '食品安全'] = 1
df.loc[df['website']=='NYTimes', '無關'] = 1
df.to_excel('DATA/Result_aboard_merged.xlsx')


