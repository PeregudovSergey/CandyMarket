import sqlite3
import pandas as pd

#get top10 users based on cnt tx
def top10_count_tx():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    WITH tmp (sender, cnt_tx, volume_tx) as (
      SELECT sender, COUNT(receiver) as cnt_tx, SUM(price) as volume_tx
      FROM blockchain
      GROUP BY sender
      ORDER BY cnt_tx DESC
      LIMIT 10
    )
    SELECT RANK() OVER (ORDER BY cnt_tx DESC) as rank, *
    FROM tmp
    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df

print(top10_count_tx())