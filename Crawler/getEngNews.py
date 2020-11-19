import copy, os, sys, random, time, requests, platform, datetime, re
import more_itertools
from pathlib import Path
import pandas as pd
from configparser import ConfigParser

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from urllib.request import urlparse, urljoin

from show import show
from path import path as NewsPath

pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)
pd.options.mode.chained_assignment = None  # default='warn'


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
df_cols = ['keyword', 'title', 'website', 'publish_time', 'web_url', 'news_content']


def wait():
    import random
    waittime = random.uniform(1,5)
    show(f'等待時間:{waittime}', level=2)
    time.sleep(waittime)

class readKeyWordEng(NewsPath):
    def __init__(self):
        super(readKeyWordEng, self).__init__()
        self.keywords = pd.read_excel(self.NAME.kwen).dropna()['word'].values

class NewYorkTime(readKeyWordEng):
    def __init__(self, seldate):
        super(NewYorkTime   ,   self).__init__()
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        data = pd.DataFrame(columns=df_cols)
        for keyword in self.keywords[:]:
            print(f'\n >> 搜尋關鍵字: {keyword}')
            res = pd.DataFrame(self.getNews(keyword, seldate), columns=df_cols)
            data = data.append(res)

        fn = os.path.join('DATA', 'outNews_aboard', 'NewYorkTime', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data = data
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', 'NewYorkTime', f'{seldate}.xls')
        df = pd.read_excel(fn)
        df = df.drop_duplicates(subset=['title'])

        for ii, news in df.iterrows():
            news = news.fillna('')
            url = news['web_url']
            title = news['title'].replace('\r', '')
            show(f'下載 {url}, {title}')
            content = news['news_content']
            if content != '':
                continue
            try:
                wait()
                html = requests.get(url, headers=headers)
                html = BeautifulSoup(html.text, features='lxml')
                method = {'name'     : 'section',
                          'attrs'    : {'itemprop':'articleBody'} }
                text = html.find(**method)
                text = text.find_all('p')
                text = ' '.join([i.text for i in text])
                text = re.sub('\s+|\r|\t|\n', ' ', text)        
            except:
                show('**** something wrong!! Pass it!! ****', level=1)
                text = None
            if text is None or len(text)>30000:
                df.drop(ii, axis=0)
                continue

            df.loc[ii, 'news_content'] = text
            df.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')


    def proc_url(self, keyword, time):
        url = 'https://www.nytimes.com/search?dropmab=true&endDate=TE&query=KEYWORD&sort=newest&startDate=TS'
        print(f'    網址：{url}')
        time = pd.to_datetime(time).strftime('%Y%m%d') 
        url  = url.replace('KEYWORD', keyword )
        url  = url.replace('TS'     , time)
        url  = url.replace('TE'     , time)
        self.url = url
        return url

    def getNews(self, keyword, time):
        url = self.proc_url(keyword, time)
        print(f'  >> 網址: {url}')
        try:
            html = requests.get(url, headers=headers)
            html = BeautifulSoup(html.text, features='lxml')
            print(' '*5 + '< 網頁擷取正常 >')
        except Exception as e:
            print(' '*5 + '< 網頁無法擷取，錯誤如下： >')
            print(' '*5 + f'{e}')
            return None

        newsBox  = html.find('ol', {'data-testid':'search-results'})
        newsList = newsBox.find_all('li', {'class': 'css-1l4w6pd'})

        data = []
        for ii, inews in enumerate(newsList[:]):
            newsTime = time 
            title = inews.find('h4').text
            news_url = inews.find('a')['href']
            news_url = 'https://www.nytimes.com' + news_url if news_url[0]=='/' else news_url
            print(f'     {ii+1:2d}. title: {title}')
            print(f'           url: {news_url}')
            data.append([keyword, title, 'NYTimes', newsTime, news_url, ''])
        self.tmp = data
        return data
        


class European_Commission():
    def __init__(self, seldate):
        super(European_Commission, self).__init__()
        self.seldate = seldate   
        self.run(seldate) 

    def run(self, seldate):
        url = 'https://webgate.ec.europa.eu/rasff-window/portal/?event=notificationsList&StartRow=%s'
        print(f'    網址：{url}')

        html = requests.get(url).text
        html = BeautifulSoup(html, 'lxml')
        newslist = html.find('table').find('tbody').find_all('tr')
        data = []
        cont = [(1,'Classification'), (3,'Reference'), (4,'Notifying country'),(6,'Product Category'),(7,'type'),(8,'Risk decision')]
        for inews in newslist:
            elem = inews.find_all('td')
            newsTime = pd.to_datetime(elem[2].text.strip(), format='%d/%m/%Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue 
            title = elem[5].text.strip()
            web_url = elem[-1].find('a')['href']
            news_content = f'{title}; '+ '; '.join([f'{j}: {elem[i].text.strip()}' for i,j in cont])
            
            data.append([None, title, '歐洲聯盟委員會', newsTime, web_url, news_content])

        self.data = pd.DataFrame(data, columns=df_cols)
        fn = os.path.join('DATA', 'outNews_aboard', '歐洲聯盟委員會', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

class US_fda():
    def __init__(self, seldate):
        self.seldate = seldate
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):

        url = 'https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts'
        print(f'    網址：{url}')
        cont = ( 'Brand Name(s)', 'Product Description', 'Product Type', 'Recall Reason Description', 'Company Name')

        opts = Options()
        opts.headless = True
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", headers['User-Agent'])
        driver = webdriver.Firefox(profile, executable_path='./geckodriver.exe', options=opts)
        driver.get(url) #前往這個網址
        time.sleep(2)
        elem = driver.find_element(By.CSS_SELECTOR, 'thead > tr')
        driver.execute_script("arguments[0].setAttribute('class','sorting_desc')", elem)
        table = BeautifulSoup(driver.find_element_by_css_selector('div#DataTables_Table_0_wrapper').get_attribute('innerHTML'), 'lxml')
        newslist = table.find('tbody').find_all('tr')
        data = []
        for inews in newslist:
            elems = inews.find_all('td')
            newsTime = pd.to_datetime(elems[0].text.strip(), format='%m/%d/%Y')
            title = elems[2].text.strip()
            web_url = urljoin('https://www.fda.gov/', elems[1].find('a')['href'])
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue 
            #news_content = '; '.join([f'{j}: {elems[i].text.strip()}' for i,j in zip(range(1,7), cont)])
            data.append([None, title, '美國食品藥品監督管理局', newsTime, web_url, None])

        self.data = pd.DataFrame(data, columns=df_cols)
        fn = os.path.join('DATA', 'outNews_aboard', '美國食品藥品監督管理局', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '美國食品藥品監督管理局', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url, headers=headers).text
                    html = BeautifulSoup(html, 'lxml')
                    cont = html.find('div', {'class': 'col-md-8 col-md-push-2'}) 
                    cont = ' '.join([i.text for i in cont.find_all('p')])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

        
        
class Hongkong_cfs():
    def __init__(self, seldate):
        self.run1(seldate)
        self.run2(seldate)
        #self.getContent(seldate)
        

    def run1(self, seldate):
        url = 'https://www.cfs.gov.hk/tc_chi/whatsnew/whatsnew_fa/whatsnew_fa.html'
        print(f'    網址：{url}')
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        self.html = html
        newslist = html.find('tbody').find_all('tr')[1:]
        data = []
        for inews in newslist:
            elems = inews.find_all('td')
            newsTime = pd.to_datetime(elems[0].text.strip(), format='%d.%m.%Y')
            #if newsTime.strftime('%Y-%m-%d') != seldate:
            if newsTime.strftime('%Y-%m-%d') < seldate:
                continue
                
            title = elems[1].text.strip()
            web_url = urljoin('https://www.cfs.gov.hk/', elems[1].find('a')['href'])
            data.append([None, title, '香港食物安全中心', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

    def run2(self, seldate):
        url = 'https://www.cfs.gov.hk/tc_chi/rc/subject/fi_list.html'
        print(f'    網址：{url}')
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        self.html = html
        newslist = html.find('tbody').find_all('tr')[1:]
        data = []
        for inews in newslist:
            elems = inews.find_all('td')
            newsTime = pd.to_datetime(elems[0].text.strip(), format='%d.%m.%Y')
            #if newsTime.strftime('%Y-%m-%d') != seldate:
            if newsTime.strftime('%Y-%m-%d') < seldate:
                continue
                
            title = elems[1].text.strip()
            web_url = urljoin('https://www.cfs.gov.hk/', elems[1].find('a')['href'])
            data.append([None, title, '香港-食物安全中心', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = pd.concat([self.data, data])

        fn = os.path.join('DATA', 'outNews_aboard', '香港食物安全中心', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '香港食物安全中心', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('div', {'id': 'content'}).find('table').find_all('td')
                    cont = ' '.join([''.join(i.text.split()) for i in cont])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

class CAfoodRecall():
    def __init__(self, seldate):
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        url = 'https://www.inspection.gc.ca/about-cfia/newsroom/food-recall-warnings/eng/1299076382077/1299076493846'
        print(f'    網址：{url}')
        html = requests.get(url)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('tbody').find_all('tr')
        self.newslist = newslist

        data = []
        for inews in newslist:
            elems = inews.find_all('td')
            newsTime = pd.to_datetime(elems[0].text.strip(), format='%Y-%m-%d')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue
                
            title = ' '.join(elems[1].text.split())
            web_url = urljoin('https://www.inspection.gc.ca/', elems[1].find('a')['href'])
            data.append([None, title, '加拿大食物檢驗局', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '加拿大食物檢驗局', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '加拿大食物檢驗局', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('table').find_all('td')
                    cont = ' '.join([' '.join(i.text.split()) for i in cont])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

class Ireland_fsai():
    def __init__(self, seldate):
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        url = 'https://www.fsai.ie/news_centre/food_alerts.html'
        print(f'    網址：{url}')
        html = requests.get(url)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('div', {'id': 'content'}).find_all('div', {'class': 'news-listing'})
        self.newslist = newslist
        
        data = []
        for inews in newslist:
            elems = inews.find('p', {'class': 'title'})
            newsTime = pd.to_datetime(elems.find('em').text.strip(), format='%A, %d %B %Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue

            title = elems.find('a').text.strip()
            web_url = urljoin('https://www.fsai.ie/', elems.find('a')['href'])
            data.append([None, title, '愛爾蘭食品安全局', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '愛爾蘭食品安全局', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '愛爾蘭食品安全局', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('div', {'id': 'content'})
                    cont = ' '.join([i.text.strip() for i in cont.find_all('p')]) 
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

class European_efsa():
    def __init__(self, seldate):
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        url = 'http://www.efsa.europa.eu/en/news/61826'
        print(f'    網址：{url}')
        html = requests.get(url)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('div', {'class': 'view-content news-page-display'}).find_all('div', {'class':'views-row'})
        self.newslist = newslist
        
        data = []
        for inews in newslist:
            newsTime = inews.find('div', {'class':'views-field views-field-field-published-date'}).find('span').text.strip()
            newsTime = pd.to_datetime(newsTime, format='%d %B %Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue

            elems = inews.find('div', {'class':'views-field views-field-title'}) 
            title = elems.find('a').text 
            web_url = urljoin('http://www.efsa.europa.eu/', elems.find('a')['href'])
            data.append([None, title, '歐洲食品安全管理局', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '歐洲食品安全管理局', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '歐洲食品安全管理局', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('div', {'class': 'field field--name-body field--type-text-with-summary field--label-hidden'})
                    cont = ' '.join([i.text for i in cont.find_all('p')])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

class US_foodSafty():
    def __init__(self, seldate):
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        url = 'https://www.foodsafetynews.com/foodborne-illness-outbreaks/'
        print(f'    網址：{url}')
        html = requests.get(url, headers=headers)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('div', {'id': 'lxb_af-loop'}).find_all('div', {'class':'lxb_af-grid-magazine-row'})
        newslist = list(more_itertools.flatten([i.find_all('article') for i in newslist]))
        self.newslist = newslist
        data = []
        for inews in newslist:
            newsTime = inews.find('time').text 
            newsTime = pd.to_datetime(newsTime, format='%B %d, %Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue

            title = inews.find('h1').find('a').text 
            web_url = urljoin('https://www.foodsafetynews.com/', inews.find('h1').find('a')['href'])
            data.append([None, title, '美國食品安全新聞', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '美國食品安全新聞', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '美國食品安全新聞', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url, headers=headers)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('div', {'id':'lxb_af-loop'})
                    cont = ' '.join([' '.join(i.text.split()) for i in cont.find_all('p')])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

class UK_food():
    def __init__(self, seldate):
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        url = 'https://www.food.gov.uk/news-alerts/search'
        print(f'    網址：{url}')
        html = requests.get(url, headers=headers)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('div', {'id':'block-mainpagecontent'}).find_all('div', {'class':'views-row'})
        self.newslist = newslist
        data = []
        for inews in newslist:
            newsTime = inews.find('span', {'class':'field field__created'}).text
            newsTime = pd.to_datetime(newsTime, format='%d %B %Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue

            title = inews.find('a').text 
            web_url = urljoin('https://www.food.gov.uk/', inews.find('a')['href'])
            data.append([None, title, '英國食品標準管理局', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '英國食品標準管理局', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '英國食品標準管理局', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url, headers=headers)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('div', {'id':'block-mainpagecontent'})
                    cont = ' '.join([' '.join(i.text.split()) for i in cont.find_all('p')])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

class Macau_food():
    def __init__(self, seldate):
        self.run(seldate)

    def run(self, seldate):
        url = 'https://www.foodsafety.gov.mo/c/foodalert/table'
        print(f'    網址：{url}')
        html = requests.get(url, headers=headers)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('tbody').find_all('tr')
        self.newslist = newslist
        data = []
        for inews in newslist:
            elems = inews.find_all('td')
            newsTime = elems[1].text.strip()
            newsTime = pd.to_datetime(newsTime, format='%d/%m/%Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue

            title = elems[0].find('a').text 
            web_url = urljoin('https://www.foodsafety.gov.mo/', elems[0].find('a')['href'])
            data.append([None, title, '澳門特別行政區政府食品安全資訊', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '澳門特別行政區政府食品安全資訊', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

class AU_food():
    def __init__(self, seldate):
        self.run(seldate)
        self.getContent(seldate)

    def run(self, seldate):
        url = 'http://www.foodstandards.gov.au/industry/foodrecalls/recalls/Pages/default.aspx'
        print(f'    網址：{url}')
        html = requests.get(url, headers=headers)
        html.encoding= 'utf-8'
        html = BeautifulSoup(html.text, 'lxml')
        newslist = html.find('div', {'id': 'ctl00_ctl45_g_76f28544_b3c4_43f4_b435_13e7b563f7f1'}).find_all('table')[1:]
        self.newslist = newslist
        self.html = html
        data = []
        for inews in newslist:
            newsTime = inews.find('div', {'style': 'float: right'}).text.strip()
            newsTime = pd.to_datetime(newsTime, format='%d/%m/%Y')
            if newsTime.strftime('%Y-%m-%d') != seldate:
            #if newsTime.strftime('%Y-%m-%d') < seldate:
                continue

            title = inews.find('h3').find('a').text 
            web_url = urljoin('http://www.foodstandards.gov.au/', inews.find('h3').find('a')['href'])
            data.append([None, title, '澳洲紐西蘭食物標準', newsTime, web_url, None])
        data = pd.DataFrame(data, columns=df_cols)
        self.data = data

        fn = os.path.join('DATA', 'outNews_aboard', '澳洲紐西蘭食物標準', f'{seldate}.xls')
        Path(os.path.dirname(fn)).mkdir(parents=True, exist_ok=True)
        self.data.to_excel(fn, index=False)
        print(f'完成，擷取資料如下\n{self.data}')

    def getContent(self, seldate):
        fn = os.path.join('DATA', 'outNews_aboard', '澳洲紐西蘭食物標準', f'{seldate}.xls')
        df = pd.read_excel(fn).fillna('')
        for ii, line in df.iterrows():
            if line['news_content'] == '':
                url = line['web_url']
                try:
                    html = requests.get(url, headers=headers)
                    html.encoding = 'utf-8'
                    html = BeautifulSoup(html.text, 'lxml')
                    cont = html.find('div', {'class':'article-content'})
                    cont = ' '.join([' '.join(i.text.split()) for i in cont.find_all('p')])
                except Exception as e:
                    print(e)
                    cont = None
                df.loc[ii, 'news_content'] = cont
            df.to_excel(fn, index=False)

if __name__ == '__main__':
    
    random = False

    run = {'紐約時報'                       : NewYorkTime
          ,'歐洲聯盟委員會'                 : European_Commission
          ,'美國食藥局'                     : US_fda
          ,'香港食物安全中心'               : Hongkong_cfs
          ,'加拿大食物檢驗局'               : CAfoodRecall
          ,'愛爾蘭食品安全局'               : Ireland_fsai
          ,'歐洲食品安全管理局'             : European_efsa
          ,'美國食品安全新聞'               : US_foodSafty
          ,'英國食品標準管理局'             : UK_food
          ,'澳門特別行政區政府食品安全資訊' : Macau_food
          ,'澳洲紐西蘭食物標準'             : AU_food}

    whichday, newsName = sys.argv[1:3]

    assert newsName in run.keys(), f'新聞名稱錯誤，請給定正確的新聞名稱: {", ".join(run.keys())}'
    print(f'     -----> 國際新聞爬蟲：{newsName}')

    r = run[newsName](whichday)


'''
 '紐約時報'                              'https://www.nytimes.com/search?dropmab=true&endDate=TE&query=KEYWORD&sort=newest&startDate=TS'
 '歐洲聯盟委員會'                        'https://webgate.ec.europa.eu/rasff-window/portal/?event=notificationsList&StartRow=%s'
 '美國食藥局'                            'https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts'
 '香港食物安全中心'                      'https://www.cfs.gov.hk/tc_chi/whatsnew/whatsnew_fa/whatsnew_fa.html'
                                         'https://www.cfs.gov.hk/tc_chi/rc/subject/fi_list.html'
 '加拿大食物檢驗局'                      'https://www.inspection.gc.ca/about-cfia/newsroom/food-recall-warnings/eng/1299076382077/1299076493846'
 '愛爾蘭食品安全局'                      'https://www.fsai.ie/news_centre/food_alerts.html'
 '歐洲食品安全管理局'                    'http://www.efsa.europa.eu/en/news/61826'
 '美國食品安全新聞'                      'https://www.foodsafetynews.com/foodborne-illness-outbreaks/'
 '英國食品標準管理局'                    'https://www.food.gov.uk/news-alerts/search'
 '澳門特別行政區政府食品安全資訊'        'https://www.foodsafety.gov.mo/c/foodalert/table'
 '澳洲紐西蘭食物標準'                    'http://www.foodstandards.gov.au/industry/foodrecalls/recalls/Pages/default.aspx'
'''
