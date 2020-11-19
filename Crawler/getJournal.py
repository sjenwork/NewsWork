import copy, os, sys, random, time, requests, platform, datetime, re
import pandas as pd
from bs4 import BeautifulSoup
from configparser import ConfigParser
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from show import show
from path import path as NewsPath

pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)
pd.options.mode.chained_assignment = None  # default='warn'


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
columns = ['Keyword', 'title', 'website', 'publish_date', 'publish_time', 'update_time', 'Authors', 'web_url', 'news_content']

''' ------------------------------------------------------------'''
'''              讀取系統名稱，並載入自定義工具                 '''
''' ------------------------------------------------------------'''

def wait():
    if random:
        waittime = random.uniform(1,5)
    else:
        waittime = 0.5
    #show(f'等待時間:{waittime}', level=2)
    time.sleep(waittime)

class readKeyWordChn(NewsPath):
    def __init__(self):
        super(readKeyWordChn, self).__init__()
        self.keywords = pd.read_excel(self.NAME.kwch)['word'].values

class readKeyWordEng(NewsPath):
    def __init__(self):
        super(readKeyWordEng, self).__init__()
        self.keywords = pd.read_excel(self.NAME.kwen).dropna()['word'].values



class downloadJournalText():
    def __init__(self, JournalName):
        super(downloadJournalText, self).__init__()
        self.fileName = os.path.join('DATA', 'Journal', JournalName, f'{today.strftime("%Y-%m-%d")}.xls')
        self._downloadText()

    def _downloadText(self):
        data = pd.read_excel(self.fileName)
        data = data.fillna('')
        content = data['news_content']
        title   = data['title']
        print('  ------------------------------------------------------')
        print('    >> 下載期刊內容')
        
        for i,news in data.iterrows():
            if content[i] != '':
                print(f'      >>>> {title[i][:60]}... 已經下載過，不需重複下載。')
                continue

            print(f'     >>>> 下載 {news[1][:60]} {news[6]}')

            url = news['web_url']
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                html = requests.get(url, headers=headers)
                html = BeautifulSoup(html.text, features='lxml')
            except:
                print('      **** something wrong!! Restart it!! ****')
           
            method = {'name' : 'div',
                      'attrs': {'class':'abstract author'} }
            text = html.find(**method)

            if text is not None:
                text = text.find('p').text
            else:
                text = ''
            content[i] = text
            data['news_content'] = content
            data.to_excel(self.fileName, index=False)

        #title = pd.DataFrame(self.TitleHist, columns=['title']).append(data.title.to_frame())
        #title = title.drop_duplicates().reset_index(drop=True)
        #title.to_excel(self.JournalHistFile, index=False)

        self.data = data


class envJournal():
    def __init__(self, JournalName, **kwargs):
        self.JournalName = JournalName 

        keywords = readKeyWordEng().keywords[:]
        self.loop(keywords, JournalName)

    def loop(self, keywords, name):

        self.data = pd.DataFrame(columns = columns)
        for keyword in keywords[:]:
            self.getList(keyword, name)

        fileName = os.path.join('DATA', 'Journal', self.JournalName, f'{today.strftime("%Y-%m-%d")}.xls') 
       
        Path(os.path.dirname(fileName)).mkdir(parents=True, exist_ok=True)

        self.data = self.data.drop_duplicates().reset_index(drop=True)
        self.data.to_excel(fileName, index=False)

    def getList(self, keyword, name):
        print(f'   -----  搜尋關鍵字 "{keyword}" -----' )
        keyword = keyword.replace(' ','%20')
        name = name.replace('_', '%20')
        website = f'https://www.sciencedirect.com/search?qs={keyword}&pub={name}&sortBy=date&show=100'

        print(f'     網址:  {website}')
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        newsBox = html.find('div', {'id':'srp-results-list'})
        if newsBox is None:
            print('   未找到任何新聞\n')
            return
        newsList = newsBox.find_all('li', {'class':'ResultItem col-xs-24 push-m'})

        for inews in newsList:
            title = inews.find('h2').find('a').text
            try:
                try:
                    time = inews.find('div', text=re.compile('First available on .*')).text
                    time = datetime.datetime.strptime(time, 'First available on %d %B %Y') 
                    
                except :
                    time = inews.find('span', text=re.compile('Available online .*')).text
                    time = datetime.datetime.strptime(time, 'Available online %d %B %Y') 
            except:
                print(f'    >> 無法找到時間，直接擷取')
                time = today
                if len(self.data)>=20:
                    break

            if time < today - datetime.timedelta(3):
                print(f'   後續之新聞之日期早於{(today - datetime.timedelta(3)).strftime("%Y-%m-%d")}，超出擷取日期之範圍\n')
                break

            newsTime  = time.strftime('%Y-%m-%d') 
            volume    = inews.find('div', {'class':'SubType hor'}).find_all('span')[2].text
            authors    = inews.find('ol' ).text
            #author    = ''

            url   = 'https://www.sciencedirect.com' + inews.find('a')['href']
            print(f'     >>>> {newsTime}  {title[:70]}... {url}')

            # 1.Keyword  2.title 3.website 4.publish_date 5.publish_time 6.update_time 7.Authors 8.web_url 9.news_content
            #        1                            2      3                                       4          5         6     7       8     9 
            data = [[keyword.replace('%20', ' '), title, 'Journal: ' + name.replace('%20', ' '), newsTime , newsTime, None, authors, url, '', ]]
            data = pd.DataFrame(data, columns=columns)
            self.data = self.data.append(data)
            
            #break 
            
        self.html = html
        self.newsBox = newsBox
        self.newsList = newsList
            


if __name__ == '__main__':

    JournalList = [ 'Environmental_Pollution', 
                    'Environmental_Research', 
                    'Environment_International', 
                    'Science_of_the_total_environment', 
                    'Journal_of_Food_and_Drug_Analysis' ]

    #today = datetime.datetime.today()
    today = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
    for journal in JournalList[:]:
        J = envJournal(journal)
        d = downloadJournalText(journal)
