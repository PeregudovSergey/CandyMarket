import sqlite3
import pandas as pd

#gas + reward
def miner_profit():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    SELECT miner, SUM(gas) + MIN(reward) as miner_profit
    FROM block_info JOIN blockchain 
    ON block_info.id_block = blockchain.id_block
    GROUP BY miner
    ORDER BY miner_profit
    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df
