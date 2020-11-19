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


''' ------------------------------------------------------------'''
'''                     共用函數                                '''
''' ------------------------------------------------------------'''

def wait():
    if random:
        waittime = random.uniform(1,5)
    else:
        waittime = 0.5
    #show(f'等待時間:{waittime}', level=2)
    time.sleep(waittime)

class NameList(NewsPath):
    def __init__(self):
        super(NameList, self).__init__()
        self._NewsTable()
 
    def _NewsTable(self):
        self.newsTable = {'自由時報電子報'      : 'LibertyTimesNet'
                         ,'中國時報電子報'      : 'chinaTimes'
                         ,'農傳媒'              : 'agriharvest'
                         ,'聯合新聞網'          : 'udn'
                         ,'蘋果日報'            : 'AppleDaily'
                         ,'中央通訊社'          : 'CNA'
                         ,'東森新聞報'          : 'ETtoday'
                         ,'食力'                : 'foodNEXT'
                         ,'美國紐約時報'        : 'NYTimes'
                         ,'European_Commission' : 'European_Commission'
                         ,'US_FDA'              : 'us_fda'
                         }

    def getOPath(self, news, time):
        name = self.newsTable[news]
        name = os.path.join(self.NAME.oput).replace('NEWS', name).replace('TIME', time)
        Path(name).parents[0].mkdir(parents=True, exist_ok=True)
        return name


class readKeyWordChn(NewsPath):
    def __init__(self):
        super(readKeyWordChn, self).__init__()
        self.keywords = pd.read_excel(self.NAME.kwch)['word'].values

class readKeyWordEng(NewsPath):
    def __init__(self):
        super(readKeyWordEng, self).__init__()
        self.keywords = pd.read_excel(self.NAME.kwen).dropna()['word'].values


#colName = lambda : ['關鍵字', '標題', '網站', '發布日期時間', '網址', '內文']
colName = lambda : ['keyword', 'title', 'website', 'publish_time', 'web_url', 'news_content']
getTsta = lambda date: pd.to_datetime(date + ' 07:00') - pd.Timedelta(hours=24)
getTend = lambda date: pd.to_datetime(date + ' 07:00')



class downloadNewsText(NameList):
    def __init__(self, NewsName, whichday):
        super(downloadNewsText, self).__init__()
        self.whichday = whichday
        self.NewsName = NewsName
        self.__downloadContent__()

    def __readNews__(self):
        self.fileName = self.getOPath(self.NewsName, self.whichday)
        return pd.read_excel(self.fileName).fillna('')

    def __downloadContent__(self):
        show('------------------------------------------------------', level=1, sign='')
        show('下載新聞內容')

        data = self.__readNews__()
        content = data['news_content']
        html = None
        url = None
        for i,news in data.iterrows():
            #if i >1: continue
            if content[i] != '':
                continue
            url = news['web_url']
            NewsText = news['title'].replace('\r', '')
            show(f'下載 {news["web_url"]}, {news["title"]}')
            try:
                wait()
                html = requests.get(url, headers=headers)
                html = BeautifulSoup(html.text, features='lxml')
                text = self._method(html, url)
            except:
                text = None

            content[i] = text
            data['news_content'] = content
            data.to_excel(self.fileName, index=False)

    def _method(self, html, url):
        text = None
        if self.NewsName == '農傳媒': 
            # need being modified
            text = html.find_all('div', 
                    {'class' :'tdb-block-inner td-fix-index'})
            if text is not None and len(text) >=5:
                text = text[5].text
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。', level=2)
                text = None

        elif self.NewsName == '中央通訊社':
            text = html.select_one('article  div.centralContent')
            try:
                text = text.text
            except:
                text = None

        elif self.NewsName == '自由時報電子報':
            methods = [{'name'     : 'div',
                        'attrs'    : {'itemprop':'articleBody'} }
                      ,{'name'     : 'div',
                        'attrs'    : {'data-desc':'內文'} }
                      ,{'name'     : 'div',
                        'attrs'    : {'class':'text'} }
                      ]
            for method in methods:
                text = html.find(**method)
                if text is not None:
                    break

            if text is not None:
                text = text.find_all('p')
                text = ''.join([i.text for i in text if not i.attrs])
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。')
                text = None
			
        elif self.NewsName == '東森新聞報':
            method = {'name'     : 'div',
                      'attrs'    : {'class':'story'} }
            text = html.find(**method)

            if text is not None:
                text = text.find_all('p')
                text = ''.join([i.text for i in text])
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。')
                text = None

        elif self.NewsName == '食力':
            method = {'name'     : 'div',
                      'attrs'    : {'class': 'post-content'} }
            text = html.find(**method)

            if text is not None:
                text = text.find_all('p')
                text = ''.join([i.text for i in text])
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。')
                text = None

        elif self.NewsName == '中國時報電子報':
            method = {'name'     : 'div',
                      'attrs'    : {'class':'article-body'} }
            text = html.find(**method)
            if text is not None:
                text = text.text
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。')
                text = None

        elif self.NewsName == '聯合新聞網':
            if url.split('//')[1].split('.')[0] == 'udn':
                method = {'name'     : 'article',
                          'attrs'    : {'class':'article-content'} }
            elif url.split('//')[1].split('.')[0] == 'health':
                method = {'name'     : 'div',
                          'attrs'    : {'id':'story_body_content'} }
            elif url.split('//')[1].split('.')[0] == 'stype':
                method = {'name'     : 'div',
                          'attrs'    : {'id':'con'} }
            elif url.split('//')[1].split('.')[0] == 'house':
                method = {'name'     : 'div',
                          'attrs'    : {'id':'story_body_content'} }
            else:
                method = {'name'     : None,
                          'attrs'    : {'id':None} }
                
            text = html.find(**method)
            
            if text is not None:
                text = ''.join([i.text for i in text.find_all('p')])
                text = re.sub('[\n\r\s]+', '', text)
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。')
                text = None

        elif self.NewsName == '蘋果日報':
            method = {'name'     : 'div',
                      'attrs'    : {'id':'articleBody'} }
            text = html.find(**method)
            if text is not None:
                text = text.find_all('p')
                text = ''.join([i.text for i in text])
            else:
                show('找不到新聞內容，可能是新聞需要付費。')
                text = None

        elif self.NewsName == '美國紐約時報':
            method = {'name'     : 'section',
                      'attrs'    : {'itemprop':'articleBody'} }
            text = html.find(**method)

            if text is not None:
                text = text.find_all('p')
                text = ' '.join([i.text for i in text])
            else:
                show('找不到新聞內容，可能是新聞的格式不同所致。')
                text = None


        if text is not None:
            text = re.sub('\s+|\r|\t|\n', ' ', text)
        return text



class WebDriver():
    def __init__(self):
        self._run()

    def _run(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", headers['User-Agent'])
        osName = platform.platform().split('-')[0]
        if osName == 'Windows':
            self.driver = webdriver.Firefox(profile, executable_path='./geckodriver.exe')
        elif osName == 'Darwin':
            self.driver = webdriver.Firefox(profile, executable_path='./geckodriver')
        else:
            raise valueError('請確認執行環境，目前之環境不屬於以定義之Windows或Darwin')

    def _wait(self, By, element):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By, element))
            )
        finally:
            self.driver.quit()

'''
    以下為各家電子新聞之函數
''' 
class foodNEXT(readKeyWordChn, WebDriver, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '食力'
        self.website = 'https://www.foodnext.net/search'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn    , self).__init__()
        super(WebDriver         , self).__init__()
        super(foodNEXT          , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', sign='', level=4, nlb=True)
        print('  ------------------------------------------------------')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                print('  ------------------------------------------------------')
                print(f'    >> 搜尋關鍵字:"{keyword}"; 網址:"{website}"')
                try:
                    self.driver.get(website) #前往這個網址
                    self.driver.find_elements(by=By.CSS_SELECTOR, value='input[type=text][name=query]')[1].send_keys(keyword)
                    self.driver.find_elements(by=By.CSS_SELECTOR, value='.btn.btn-teal.btn-squared')[0].click()
                except:
                    print('      **** something wrong!! Restart it!! ****')
                    WebDriver.__init__(self)
                    self.driver.implicitly_wait(30)
                    self.driver.get(website) #前往這個網址
                    self.driver.find_elements(by=By.CSS_SELECTOR, value='input[type=text][name=query]')[1].send_keys(keyword)
                    self.driver.find_elements(by=By.CSS_SELECTOR, value='.btn.btn-teal.btn-squared')[0].click()
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                #nextPage = False
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)


    def _getKeywordNews_sub(self, keyword):
        self.driver.implicitly_wait(30)
        newsBox = BeautifulSoup(self.driver.find_element(By.CSS_SELECTOR, 'div.search-classic').get_attribute('innerHTML'))
        self.newsBox = newsBox
        self.newsList = newsList = newsBox.find_all('li')

        nextPage = True
        for inews in newsList[:]:
            Time = inews.find('p', {'class':'date'}).text
            Time = re.match('(.*[0-9])\s+', Time).group(1) 
            newsTime = pd.to_datetime(Time)
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find('h4').text)
            url   = inews.find('a')['href']
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class CNA(readKeyWordChn, WebDriver, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '中央通訊社'
        self.website = 'https://www.cna.com.tw/search/hysearchws.aspx?q=KEYWORD'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn    , self).__init__()
        super(WebDriver         , self).__init__()
        super(CNA               , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', sign='', level=4, nlb=True)
        print('  ------------------------------------------------------')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                print('  ------------------------------------------------------')
                print(f'    >> 搜尋關鍵字:"{keyword}"; 網址:"{website}"')
                try:
                    self.driver.get(website) #前往這個網址
                except:
                    print('      **** something wrong!! Restart it!! ****')
                    WebDriver.__init__(self)
                    self.driver.implicitly_wait(30)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)


    def _getKeywordNews_sub(self, keyword):
        self.driver.implicitly_wait(30)
        newsBox = self.driver.find_element(By.CSS_SELECTOR, 'div.centralContent  #jsMainList')
        self.newsList = newsList = newsBox.find_elements(By.CSS_SELECTOR, 'li')

        nextPage = True
        for inews in newsList[:]:
            Time  = inews.find_element(By.CSS_SELECTOR, 'li a div div').text
            newsTime = pd.to_datetime(Time)
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find_element(By.CSS_SELECTOR, 'li a').text)
            url   = inews.find_element(By.CSS_SELECTOR, 'li a').get_attribute('href')
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class LibertyTimesNet(readKeyWordChn, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '自由時報電子報'
        #self.website = 'https://news.ltn.com.tw/search?keyword=KEYWORD&conditions=and&start_time=TS&end_time=TE&page=PAGE'
        self.website = 'https://search.ltn.com.tw/list?keyword=KEYWORD&start_time=TS&end_time=TE&sort=date&type=all&page=PAGE'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(LibertyTimesNet   , self).__init__()
        super(readKeyWordChn    , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()

    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', sign='', level=4, nlb=True)
        show('------------------------------------------------------', level=1, sign='')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 10):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                website = website.replace('PAGE'   , str(page))
                website = website.replace('TS'     , self.Tstart.strftime('%Y-%m-%d'))
                website = website.replace('TE'     , self.Tend.strftime('%Y-%m-%d'))
                show('------------------------------------------------------', level=1, sign='')
                show(f'搜尋關鍵字:"{keyword}"; 網址:"{website}"', level=1)
                try:
                    self._getInfo(website) 
                except:
                    show('**** something wrong!! Restart it!! ****', level=1)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)

    def _getInfo(self, website):
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        self.html = html

    def _getKeywordNews_sub(self, keyword):
        newsBox = self.html.find('ul', {'class': 'list boxTitle'})
        if newsBox is None:
            return False

        self.newsList = newsList = newsBox.find_all('li')

        nextPage = True
        for inews in newsList[:]:
            Time  = inews.find('span').text
            Time = re.match('(.*)小時前', Time)
            if Time is None:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            Time = Time.group(1)
            newsTime = datetime.datetime.now() - datetime.timedelta(hours=int(Time))
            #newsTime = pd.to_datetime(Time) 
            #newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            #if newsTime2.strftime('%Y-%m-%d') < self.whichday:
            #    show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
            #    nextPage = False
            #    break
            title = re.sub('[^\w]', ' ', inews.find('a', {'class': 'tit'}).text)
            url   = inews.find('a')['href']
            show(f'文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class ETtoday(readKeyWordChn, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '東森新聞報'
        self.website = 'https://www.ettoday.net/news_search/doSearch.php?keywords=KEYWORD&idx=1&page=PAGE'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn    , self).__init__()
        super(ETtoday        , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', level=4, sign='', nlb=True)
        show('------------------------------------------------------', level=1, sign='')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                website = website.replace('PAGE'   , str(page))
                show('------------------------------------------------------', level=1, sign='')
                show(f'搜尋關鍵字:"{keyword}"; 網址:"{website}"', level=1)
                try:
                    self._getInfo(website)
                except:
                    show('**** something wrong!! Restart it!! ****', level=1)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)

    def _getInfo(self, website):
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        self.html = html

    def _getKeywordNews_sub(self, keyword):
        newsList = self.html.find_all('div', {'class':'archive clearfix'}) 

        nextPage = True
        for inews in newsList[:]:
            Time = inews.find('span').text
            Time = re.match('.*([0-9]{4}.*[0-9]{2})', Time).group(1)
            newsTime = pd.to_datetime(Time)
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find('h2').text)
            url   = inews.find('a')['href']
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage



class ChinaTimes(readKeyWordChn, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '中國時報電子報'
        self.website = 'https://www.chinatimes.com/search/KEYWORD?page=PAGE&chdtv'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn    , self).__init__()
        super(ChinaTimes        , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', level=4, sign='', nlb=True)
        show('------------------------------------------------------', level=1, sign='')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 10):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                website = website.replace('PAGE'   , str(page))
                show('------------------------------------------------------', level=1, sign='')
                show(f'搜尋關鍵字:"{keyword}"; 網址:"{website}"', level=1)
                try:
                    self._getInfo(website)
                except:
                    show('**** something wrong!! Restart it!! ****', level=1)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)

    def _getInfo(self, website):
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        self.html = html

    def _getKeywordNews_sub(self, keyword):
        newsBox = self.html.find_all('ul', {'class':'vertical-list list-style-none'})
        if len(newsBox) != 1:
            show('get more than 1 element. Please confirm.')
            return
        self.newsBox = newsBox
        self.newsList = newsList = newsBox[0].find_all('li')

        nextPage = True
        for inews in newsList[:]:
            Time  = inews.find('time').text
            newsTime = pd.to_datetime(Time,  format='%H:%M%Y/%m/%d') #10:002020/04/16
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find('h3').text)
            url   = inews.find('a')['href']
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class Agriharvest(readKeyWordChn, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '農傳媒'
        self.website = 'https://agriharvest.tw/page/PAGE?s=KEYWORD'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn   , self).__init__()
        super(Agriharvest      , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', sign='', level=4, nlb=True)
        show('------------------------------------------------------', level=1, sign='')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                website = website.replace('PAGE'   , str(page))
                show('------------------------------------------------------', level=1, sign='')
                show(f'搜尋關鍵字:"{keyword}"; 網址:"{website}"', level=1)
                try:
                    self._getInfo(website)
                except:
                    show('**** something wrong!! Restart it!! ****', level=1)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)

    def _getInfo(self, website):
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        self.html = html

    def _getKeywordNews_sub(self, keyword):
        newsBox = self.html.find_all('div', {'class':'td-ss-main-content'})
        if len(newsBox) != 1:
            show('get more than 1 element. Please confirm.')
            return
        self.newsBox = newsBox
        self.newsList = newsList = newsBox[0].find_all('div', {'class' : 'td-block-span4'})

        nextPage = True
        for inews in newsList[:]:
            Time = inews.find('time')['datetime']
            newsTime = pd.to_datetime(Time).tz_localize(None)
            self.newsTime = newsTime
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find('h3').text)
            url   = inews.find('h3').find('a')['href']
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class UDN(readKeyWordChn, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '聯合新聞網'
        self.website = 'https://udn.com/search/word/2/KEYWORD'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn, self).__init__()
        super(UDN           , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', sign='', level=4, nlb=True)
        show('------------------------------------------------------', level=1, sign='')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                website = website.replace('PAGE'   , str(page))
                show('------------------------------------------------------', level=1, sign='')
                show(f'搜尋關鍵字:"{keyword}"; 網址:"{website}"', level=1)
                try:
                    self._getInfo(website)
                except:
                    show('**** something wrong!! Restart it!! ****', level=1)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)

    def _getInfo(self, website):
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        self.html = html

    def _getKeywordNews_sub(self, keyword):
        newsBox = self.html.find_all('div', {'class':'context-box__content story-list__holder story-list__holder--full'})
        if len(newsBox) != 1:
            show('get more than 1 element. Please confirm.')
            return
        self.newsBox = newsBox
        self.newsList = newsList = newsBox[0].find_all('div', {'class' : 'story-list__news'})

        nextPage = True
        for inews in newsList[:]:
            Time = inews.find('time').text
            newsTime = pd.to_datetime(Time).tz_localize(None)
            self.newsTime = newsTime
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find('h2').find('a').text)
            url   = inews.find('h2').find('a')['href'].replace('\n', '')
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class AppleDaily(readKeyWordChn, WebDriver, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '蘋果日報'
        self.website = 'https://tw.appledaily.com/search/KEYWORD/'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordChn    , self).__init__()
        super(WebDriver         , self).__init__()
        super(AppleDaily        , self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', sign='', level=4, nlb=True)
        print('  ------------------------------------------------------')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                print('  ------------------------------------------------------')
                print(f'    >> 搜尋關鍵字:"{keyword}"; 網址:"{website}"')
                try:
                    self.driver.get(website) #前往這個網址
                except:
                    print('      **** something wrong!! Restart it!! ****')
                    WebDriver.__init__(self)
                    self.driver.implicitly_wait(30)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                if not nextPage:
                    break

        data = self.outNews.reset_index().drop('index', axis=1)
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)


    def _getKeywordNews_sub(self, keyword):
        self.driver.implicitly_wait(30)
        newsBox = self.driver.find_elements(By.CSS_SELECTOR, 'div.stories-container')[1]
        self.newsList = newsList = newsBox.find_elements(By.CSS_SELECTOR, 'div.flex-feature')

        nextPage = True
        for inews in newsList[:]:
            Time  = inews.find_element(By.CSS_SELECTOR, 'div.timestamp').text.replace('出版時間: ','')
            newsTime = pd.to_datetime(Time)
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find_element(By.CSS_SELECTOR, 'span.desktop-blurb').text)
            url   = inews.find_element(By.CSS_SELECTOR, 'a.story-card').get_attribute('href')
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.outNews = self.outNews.append(data)
        return nextPage

class NewYorkTime(readKeyWordEng, NameList):
    def __init__(self, whichday, num=None):
        self.Name = '美國紐約時報'
        self.website = 'https://www.nytimes.com/search?dropmab=true&endDate=TE&query=KEYWORD&sort=newest&startDate=TS'
        self.whichday = whichday
        self.Tstart = getTsta(whichday)
        self.Tend   = getTend(whichday)

        super(readKeyWordEng,   self).__init__()
        super(NewYorkTime   ,   self).__init__()

        if num is not None: self.keywords = self.keywords[:num]
        self._getKeywordNews()


    def _getKeywordNews(self):
        show(f'<<< {self.Name}新聞搜尋 >>>', level=4, sign='', nlb=True)
        show('------------------------------------------------------', level=1, sign='')
        self.outNews = pd.DataFrame(columns = colName())
        for keyword in self.keywords[:]:
            for page in range(1, 2):
                website = copy.deepcopy(self.website)
                website = website.replace('KEYWORD', keyword  )
                website = website.replace('TS'     , self.yyyymmdd  )
                website = website.replace('TE'     , self.yyyymmdd  )
                show('------------------------------------------------------', level=1, sign='')
                show(f'搜尋關鍵字:"{keyword}"; 網址:"{website}"', level=1)
                try:
                    self._getInfo(website)
                except:
                    show('**** something wrong!! Restart it!! ****', level=1)
                    break
                nextPage = self._getKeywordNews_sub(keyword)
                nextPage = False
                if not nextPage:
                    break

        data = self.data.reset_index().drop('index', axis=1)
        self.data = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.data.to_excel(fileName, index=False)

    def _getInfo(self, website):
        html = requests.get(website, headers=headers)
        html = BeautifulSoup(html.text, features='lxml')
        self.html = html

    def _getKeywordNews_sub(self, keyword):
        newsBox = self.html.find_all('ol', {'data-testid':'search-results'})
        if len(newsBox) != 1:
            show('get more than 1 element. Please confirm.')
            return
        self.newsBox = newsBox
        self.newsList = newsList = newsBox[0].find_all('li', {'class': 'css-1l4w6pd'})

        nextPage = True
        for inews in newsList[:]:
            Time  = self.whichday 
            newsTime = Time 
            newsTime2 = newsTime + pd.Timedelta(days=1,hours=-7)
            if newsTime2.strftime('%Y-%m-%d') < self.whichday:
                show(f'''<<< {self.whichday} 沒有更多 "{keyword}" 相關的新聞 !!! >>>''', level=2, sign='')
                nextPage = False
                break
            title = re.sub('[^\w]', '', inews.find('h4').text)
            url = inews.find('a')['href']
            url = 'https://www.nytimes.com' + url if url[0]=='/' else url
            show(f'找到關鍵字 "{keyword}"; 文章資訊: {newsTime}, {title}, {url}', level=3)
            data = [[keyword, title, self.Name, newsTime, url, '']]
            data = pd.DataFrame(data, columns=colName())
            self.data = self.outNews.append(data)
        return nextPage

class European_Commission(NameList):
    def __init__(self, whichday):
        self.Name = 'European_Commission'
        super(European_Commission, self).__init__()
        self.whichday = whichday   
        self.run(whichday) 

    def run(self, whichday):
        url = 'https://webgate.ec.europa.eu/rasff-window/portal/?event=notificationsList&StartRow=%s'

        data = pd.read_html(requests.get(url).text)[0]
        data = data.rename({'Unnamed: 0': '#'}, axis=1)
        data = data.drop('Unnamed: 9', axis=1)
        data = data.set_index('#')
        data.index = data.index.astype(int)
        data['Date of case'] = pd.to_datetime(data['Date of case'], format='%d/%m/%Y')
        self.outNews = data

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)

class fda(NameList):
    def __init__(self, whichday, num=None):
        self.Name = 'US_FDA'
        super(fda, self).__init__()
        self.whichday = whichday
        self.run()

    def run(self):
        url = 'https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts'

        headers = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3429.49 Safari/537.36'
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", headers)
        driver = webdriver.Firefox(profile, executable_path='./geckodriver')
        driver.get(url) #前往這個網址
        time.sleep(5)
        table = driver.find_element_by_css_selector('div#DataTables_Table_0_wrapper').get_attribute('innerHTML')
        data = pd.read_html(table)[0]
    
        self.outNews = data 
        self.driver = driver

        show('檔案輸出', level=1)
        fileName = self.getOPath(self.Name, self.whichday)
        self.outNews.to_excel(fileName, index=False)


if __name__ == '__main__':
    random = False

    run = {'中國時報電子報' : ChinaTimes,
           '自由時報電子報' : LibertyTimesNet,
           '聯合新聞網'     : UDN,
           '中央通訊社'     : CNA,
           '農傳媒'         : Agriharvest, 
           '蘋果日報'       : AppleDaily, 
           '東森新聞報'     : ETtoday,
           '食力'           : foodNEXT,
            }

    
    whichday, newsName = sys.argv[1:3] 

    assert newsName in run.keys(), f'新聞名稱錯誤，請給定正確的新聞名稱: {", ".join(run.keys())}'
    print(f'     -----> 新聞爬蟲：{newsName}')

    L = run[newsName](whichday, num=10)
    d = downloadNewsText(newsName, whichday)
