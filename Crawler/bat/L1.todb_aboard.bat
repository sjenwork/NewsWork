@echo off

set curdir=S:\TV\N332-NewsWork\Crawler

cd /d %curdir%

set datestr=%date:~0,4%-%date:~5,2%-%date:~8,2%
set log=uploadaboardNews_%datestr%.log
set err=uploadaboardNews_%datestr%.err

echo 將資料上傳至db，log存放於 DATA/log/%log%
echo 當前目錄：%curdir%

python toDB_aboard.py >DATA/log/%log% 2>DATA/log/%err%
REM pause
 REM >DATA/log/%log% 2>DATA/log/%err%
REM pause