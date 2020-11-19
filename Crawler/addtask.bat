@echo off
REM schtasks /create /sc daily /tn 新聞爬蟲2.0\食力     /tr 'S:\TV\N332-NewsWork\Crawler\bat\8.foodnext.bat'    /ST 04:00
REM schtasks /create /sc daily /tn 新聞爬蟲2.0\蘋果日報 /tr 'S:\TV\N332-NewsWork\Crawler\bat\6.appledaily.bat'  /ST 05:00
REM schtasks /create /sc daily /tn 新聞爬蟲2.0\cna      /tr 'S:\TV\N332-NewsWork\Crawler\bat\4.cna.bat'         /ST 06:00

REM schtasks /create /sc daily /tn 新聞爬蟲2.0\中國時報 /tr 'S:\TV\N332-NewsWork\Crawler\bat\1.chinatimes.bat'  /ST 07:00
REM schtasks /create /sc daily /tn 新聞爬蟲2.0\自由時報 /tr 'S:\TV\N332-NewsWork\Crawler\bat\2.ltn.bat'         /ST 07:20
REM schtasks /create /sc daily /tn 新聞爬蟲2.0\udn      /tr 'S:\TV\N332-NewsWork\Crawler\bat\3.udn.bat'         /ST 07:40
REM schtasks /create /sc daily /tn 新聞爬蟲2.0\ETtoday  /tr 'S:\TV\N332-NewsWork\Crawler\bat\7.ettoday.bat'     /ST 08:00

REM schtasks /create /sc daily /tn 新聞爬蟲2.0\農傳媒   /tr 'S:\TV\N332-NewsWork\Crawler\bat\5.agriharvest.bat' /ST 08:20



REM schtasks /create /sc daily /tn 新聞爬蟲2.0\傳至db   /tr 'S:\TV\N332-NewsWork\Crawler\bat\21.todb.bat'       /ST 08:30



schtasks /create /sc daily /tn 國外新聞爬蟲\NewYorkTime                        /tr 'S:\TV\N332-NewsWork\Crawler\bat\A.NewYorkTime.bat'            /ST 17:00
schtasks /create /sc daily /tn 國外新聞爬蟲\歐洲聯盟委員會                     /tr 'S:\TV\N332-NewsWork\Crawler\bat\B.European_Commission.bat'    /ST 17:10
schtasks /create /sc daily /tn 國外新聞爬蟲\美國食藥局                         /tr 'S:\TV\N332-NewsWork\Crawler\bat\C.US_fda.bat'                 /ST 17:20
schtasks /create /sc daily /tn 國外新聞爬蟲\香港食物安全中心                   /tr 'S:\TV\N332-NewsWork\Crawler\bat\D.Hongkong_cfs.bat'           /ST 17:30
schtasks /create /sc daily /tn 國外新聞爬蟲\加拿大食物檢驗局                   /tr 'S:\TV\N332-NewsWork\Crawler\bat\E.CAfoodRecall.bat'           /ST 17:40
schtasks /create /sc daily /tn 國外新聞爬蟲\愛爾蘭食品安全局                   /tr 'S:\TV\N332-NewsWork\Crawler\bat\F.Ireland_fsai.bat'           /ST 17:50
schtasks /create /sc daily /tn 國外新聞爬蟲\歐洲食品安全管理局                 /tr 'S:\TV\N332-NewsWork\Crawler\bat\G.European_efsa.bat'          /ST 18:00
schtasks /create /sc daily /tn 國外新聞爬蟲\美國食品安全新聞                   /tr 'S:\TV\N332-NewsWork\Crawler\bat\H.US_foodSafty.bat'           /ST 18:10
schtasks /create /sc daily /tn 國外新聞爬蟲\英國食品標準管理局                 /tr 'S:\TV\N332-NewsWork\Crawler\bat\I.UK_food.bat'                /ST 18:20
schtasks /create /sc daily /tn 國外新聞爬蟲\澳門特別行政區政府食品安全資訊     /tr 'S:\TV\N332-NewsWork\Crawler\bat\J.Macau_food.bat'             /ST 18:30
schtasks /create /sc daily /tn 國外新聞爬蟲\澳洲紐西蘭食物標準                 /tr 'S:\TV\N332-NewsWork\Crawler\bat\K.AU_food.bat'                /ST 18:40


schtasks /create /sc daily /tn 國外新聞爬蟲\傳至db     /tr 'S:\TV\N332-NewsWork\Crawler\bat\L1.todb_aboard.bat'    /ST 19:00

pause



