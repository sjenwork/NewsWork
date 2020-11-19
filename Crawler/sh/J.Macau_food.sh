#!/bin/sh

news='澳門特別行政區政府食品安全資訊'

#today=`date  +'%Y-%m-%d'`
today=$1

python='/Users/jen/miniconda3/envs/work/bin/python'
path='/Users/jen/GD_simenvi/SimEnvi/Project/109E10_ChemCloud/NewsWork/Crawler'
python='/s/TV/anaconda3/python'
path='/s/TV/N332-NewsWork/Crawler'

cd $path
echo ">> $news <<"
echo "當前路徑：`pwd`"

log="DATA/log/${today}_${news}.log"
err="DATA/log/${today}_${news}.err"

echo "開始擷取網路新聞:"
${python} getEngNews.py $today $news #1>$log 2>$err
