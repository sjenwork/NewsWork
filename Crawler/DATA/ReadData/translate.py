import googletrans
import pandas as pd

translator = googletrans.Translator()

df = pd.read_excel('SearchKeyword.xls', index_col=0)
for i, text in df.iterrows():
    res = translator.translate(text.to_list()[0]).text
    #print(text.to_list()[0], res)
    df.loc[i, df.columns] = res

df.to_excel('SearchKeyword_eng.xls')
