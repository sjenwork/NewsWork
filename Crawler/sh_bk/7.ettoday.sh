#!/bin/sh

news='東森新聞報'

today=`date  +'%Y-%m-%d'`

python='/Users/jen/miniconda3/envs/work/bin/python'
path='/Users/jen/GD_simenvi/SimEnvi/Project/109E10_ChemCloud/NewsWork/Crawler'

cd $path
echo ">> $news <<"
echo "當前路徑：`pwd`"

log="DATA/log/${today}_${news}.log"
err="DATA/log/${today}_${news}.err"

echo "開始擷取網路新聞:"
${python} getNews.py $today $news 1>$log 2>$err
