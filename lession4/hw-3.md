## 3. 查國家名有"阿"字,總死亡數大於10000 
```SQL

SELECT 國家,SUM(總死亡數) AS 死亡總數
FROM world 
WHERE 國家 LIKE '%阿%'
GROUP BY 國家
HAVING SUM(總死亡數)>1000;

```
