## /* 7. 台灣有多少人在2020確診? */

```SQL
/ * 7-1方案1  */
SELECT SUM(總確診數) AS 台灣總確診數
FROM world 
WHERE 國家 = '台灣'
  AND 日期 >= '2020-01-01'::date
  AND 日期 <= '2020-12-31'::date;

/ * 7-1方案2  */
SELECT SUM(總確診數) AS 台灣總確診數
FROM world 
WHERE 國家='台灣' AND EXTRACT(YEAR FROM 日期) = 2020;

```
|  台灣2020確診數  |
|  ---------------  |
| 145,202   |