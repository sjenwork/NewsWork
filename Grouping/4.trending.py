import copy, os, sys, random, time, requests, platform, datetime, re
import pandas as pd
from bs4 import BeautifulSoup
from configparser import ConfigParser
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
import more_itertools

pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide',True)
pd.options.mode.chained_assignment = None  # default='warn'


class WebDriver():
    def __init__(self):
        self._run()

    def _run(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

        opts = Options()
        opts.headless = True
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", headers['User-Agent'])
        osName = platform.platform().split('-')[0]
        if osName == 'Windows':
            self.driver = webdriver.Firefox(profile, executable_path='./geckodriver.exe', options=opts)
        elif osName == 'Darwin':
            self.driver = webdriver.Firefox(profile, executable_path='./geckodriver', options=opts)
        else:
            raise valueError('請確認執行環境，目前之環境不屬於以定義之Windows或Darwin')

    def _wait(self, By, element):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By, element))
            )
        finally:
            self.driver.quit()


def rdKeyword(time):
    #time = '2020-09-30'
    df = pd.read_excel(f'daily_news/{time}.xlsx')['Chemical_material'].dropna()
    df = df.apply(lambda i: i.split('、'))
    chem = list(set(more_itertools.flatten(list(df))))
    return chem




if __name__ == '__main__':
    today = datetime.datetime.today()
    #today = datetime.datetime.strptime('2020-10-13', '%Y-%m-%d')
    TS = (today - datetime.timedelta(days=1)).strftime('%m/%d/%Y')
    TE = today.strftime('%m/%d/%Y') 

    #TS = '8/3/2020'
    #TE = '8/4/2020'

    #keywords = rdKeyword(today.strftime('%Y-%m-%d'))
    #keywords = ['硝酸銨', '石油', '乙醛', '甲苯', '硫磺', '萊克多巴胺']
    keywords = ['四氯乙烯', '丁酮']
    df = pd.DataFrame(keywords, columns=['化學物質'])
    df['次數'] = None 
    
    for ii, content in df.iterrows():
        text = content['化學物質']

        print(f'  >> 搜尋物質名稱"{text}"') 
        search = f'{text}[site:ptt.cc > Gossiping]'

        driver = WebDriver().driver
        print('  >> 進入google首頁')
        driver.get('https://www.google.com/')
        driver.implicitly_wait(30)
        print('  >> 尋找搜尋框並輸入搜尋字樣')
        driver.find_element(By.CSS_SELECTOR, '[title="Google 搜尋"]').send_keys(search)
        driver.implicitly_wait(30)
        print('    >> 開始搜尋')
        driver.find_element(By.CSS_SELECTOR, '[title="Google 搜尋"]').send_keys(Keys.ENTER)
        sleep(1)
        print('  >> 搜尋完成，尋找"工具"選項，並按下選單')
        driver.find_element(By.CSS_SELECTOR, '[id=hdtb-tls]').click()
        sleep(1)
        print('    >> 尋找時間區間設定選項')
        tools = driver.find_element(By.CSS_SELECTOR, '[id=hdtbMenus]')
        tools.find_elements(By.CSS_SELECTOR, 'div.mn-hd-txt')[1].click()
        sleep(1)
        print('    >> 選擇自訂時間範圍')
        select = driver.find_element(By.ID, 'lb')
        select.find_elements(By.TAG_NAME, 'g-menu-item')[6].click()
        sleep(1)
        print(f'    >> 設定搜尋時間範圍為 {TS} ~ {TE}')
        driver.find_element(By.ID, 'OouJcb').send_keys(TS)
        driver.find_element(By.ID, 'rzG2be').send_keys(TE)
        driver.find_element(By.ID, 'T3kYXe').find_element(By.TAG_NAME, 'g-button').click()
        sleep(1)
        print(f'    >> 搜尋完成。確認搜尋結果之筆數')
        foot = driver.find_element(By.ID, 'foot')
        if foot.text == '':
            try:
                newslist = driver.find_element(By.ID, 'rso')
                newslist = newslist.find_elements(By.CSS_SELECTOR, 'div[class="g"]')
                count = len(newslist)
            except:
                count = 0
        else:
            res = foot.find_element(By.TAG_NAME, 'tr').find_elements(By.TAG_NAME, 'td')
            count = (len(res)-2)*9
        
        df.loc[ii]['次數'] = count
        


