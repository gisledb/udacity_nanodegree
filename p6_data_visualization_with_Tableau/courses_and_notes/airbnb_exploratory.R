setwd('~/Documents/udacity/ipython_notebooks/p6/Project/')
getwd()

install.packages('sqldf')
library(sqldf)

sqldf('select * from airbnb limit 2')

sqldf('')

sqldf('SELECT date_collected, multiple_owner, count(1)
from (Select date_collected,host_id, count(1), 
      CASE WHEN count(1) > 1 THEN 1 END as multiple_owner
      from airbnb
      GROUP BY
      host_id, date_collected) d 
      GROUP BY date_collected, multiple_owner')

mission = sqldf('SELECT date_collected, multiple_owner, count(1) as count
from (Select date_collected,host_id, count(1), 
      CASE WHEN count(1) > 1 THEN 1 ELSE 0 END as multiple_owner
      from airbnb
      WHERE
      neighborhood = "Mission"
      GROUP BY
      host_id, date_collected) t1 
      GROUP BY date_collected, multiple_owner')


sqldf('select m1.date_collected, m2.count as single,
      m1.count as multiple, CAST(m1.count as FLOAT) / m2.count 
      from mission m1 join mission m2 on 
      m1.date_collected = m2.date_collected
      where m2.multiple_owner = 0 AND 
      m1.multiple_owner = 1',
      drv = 'rSQLite')


sqldf('select distinct(neighborhood) from airbnb')

str(airbnb)

print(colnames(airbnb))

?sqldf

sqldf('select 
      CASE
      WHEN bedrooms > 1 THEN "multi" ELSE "boh" END as bah 
      from airbnb
      limit 2')
