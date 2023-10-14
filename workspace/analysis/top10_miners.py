import sqlite3
import pandas as pd

#get top10 miners
def top10_miners():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    WITH tmp (sender, cnt_blocks) as (
      SELECT miner, COUNT(id_block) as cnt_blocks
      FROM block_info
      GROUP BY miner
      ORDER BY cnt_blocks DESC
      LIMIT 10
    )
    SELECT RANK() OVER (ORDER BY cnt_blocks DESC) as rank, *
    FROM tmp
    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df

print(top10_miners())