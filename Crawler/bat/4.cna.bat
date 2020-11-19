@echo off

set curdir=S:\TV\N332-NewsWork\Crawler

cd /d %curdir%

set news=�����q�T��
set datestr=%date:~0,4%-%date:~5,2%-%date:~8,2%
set log=getNews_%datestr%_%news%.log
set err=getNews_%datestr%_%news%.err

echo ����s�D��Ƥ��Alog�s��� DATA/log/%log%
echo ��e�ؿ��G%curdir%

python getNews.py %datestr% %news% > DATA/log/%log% 2>DATA/log/%err%
