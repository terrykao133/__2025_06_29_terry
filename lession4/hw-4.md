## /*4. 查詢哪個國家總確診數最多 */
```sql
WITH latest_date AS (
    SELECT 國家, MAX(日期) AS 最新日期
    FROM world
    GROUP BY 國家
)
SELECT 
    w.國家, w.總確診數 AS 確診總數
FROM world w
JOIN latest_date l ON w.國家 = l.國家 AND w.日期 = l.最新日期
WHERE w.iso_code NOT LIKE 'OWID%'  -- 排除全球與統計用代碼
ORDER BY 確診總數 DESC
LIMIT 1;

```
|  