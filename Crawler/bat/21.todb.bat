@echo off

set curdir=S:\TV\N332-NewsWork\Crawler

cd /d %curdir%

set datestr=%date:~0,4%-%date:~5,2%-%date:~8,2%
set log=uploadNews_%datestr%.log
set err=uploadNews_%datestr%.err

echo �N��ƤW�Ǧ�db�Alog�s��� DATA/log/%log%
echo ��e�ؿ��G%curdir%

python toDB.py
 REM >DATA/log/%log% 2>DATA/log/%err%
REM pause