SELECT B.*,CONCAT(B.ChemicalChnName,'(',B.CASNo,')') as [chemicalSet], A.[status], A.[push_status], A.[pushed_date], D.[theme_name] as [theme]
 FROM (
 SELECT TOP 5000 [id],[status],[push_status],[pushed_date] 
 FROM [ChemiBigData].[dbo].[新聞分群_國內新聞_狀態]
 WHERE [push_status] = '正常' AND [pushed_date] is null
 ORDER BY [id] DESC) A
 LEFT JOIN [dbo].[網路擷取分析_國內proc1_新聞對應化學物質] B ON A.[id] = B.[id] 
 LEFT JOIN [dbo].[新聞分群_國內新聞_結果] C ON A.[id] = C.[id] 
 LEFT JOIN [dbo].[新聞分群_主題] D ON C.[label] = D.[theme_id] 
 WHERE B.[id] is not null
 ORDER BY [id];
