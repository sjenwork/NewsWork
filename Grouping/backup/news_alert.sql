with temp as
 
(
SELECT DENSE_RANK() 
OVER( ORDER BY CAST([publish_date] AS DATE) DESC, A.[id]) AS [row], 
A.[id],[title],[news_content] AS [content],[website],	[web_url], REPLACE(CONVERT(VARCHAR, CAST([publish_date] AS DATETIME), 111), '/', '-') AS [publish_date], [keyword],  CONCAT([ChemicalChnName], '(', A.[CASNo], ')') AS [ChemicalSet], B.[label], CONCAT([theme_name], '(', [label], ')') AS [themeSet], D.[push_status], COALESCE(D.[pushed_date], '尚未推播') AS [pushed_date], D.[status], B.[lang] 

FROM (SELECT [id],[title],[news_content],[website],[web_url],[publish_date],[ChemicalChnName],[CASNo],[keyword]  
      FROM [ChemiBigData].[dbo].[網路擷取分析_國內proc1_新聞對應化學物質]  
      WHERE CAST([publish_date] AS DATE) >= '2020-08-08'  AND CAST([publish_date] AS DATE) <= '2020-09-08'  AND [in_chemistry_list] = '1') A 

JOIN (SELECT DISTINCT * FROM [ChemiBigData].[dbo].[新聞分群_國內新聞_狀態]) D 
      ON A.[id] = D.[id] AND [status] = '正常' 

LEFT JOIN [ChemiBigData].[dbo].[新聞分群_國內新聞_結果] B 
      ON A.[id] = B.[id]        

LEFT JOIN [ChemiBigData].[dbo].[新聞分群_主題] C 
      ON B.[label] = C.[theme_id]       
      WHERE 1=1  
) 

SELECT * FROM temp WHERE [row] >= 0 AND [row] < 10;
