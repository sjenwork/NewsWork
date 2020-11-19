@echo off

set curdir=S:\TV\N332-NewsWork\Crawler

cd /d %curdir%

set news=澳洲紐西蘭食物標準
set datestr=%date:~0,4%-%date:~5,2%-%date:~8,2%
set log=getNews_%datestr%_%news%.log
set err=getNews_%datestr%_%news%.err

echo 抓取新聞資料中，log存放於 DATA/log/%log%
echo 當前目錄：%curdir%

python getEngNews.py %datestr% %news% > DATA/log/%log% 2>DATA/log/%err%

