import sqlite3
import pandas as pd

#avg gas each block
def gas_analysis():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    SELECT id_block, gas, avg(gas) OVER (PARTITION BY id_block ORDER BY gas DESC) as avg_block_gas
    FROM blockchain
    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df
print(gas_analysis())