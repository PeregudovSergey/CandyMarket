import sqlite3
import pandas as pd

#get top10 users based on balance
def top10_sharks_valume():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    SELECT RANK() OVER (ORDER BY volume DESC) as rank, public_key as pk, volume
    FROM client
    ORDER BY volume DESC
    LIMIT 10
    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df
print(top10_sharks_valume()) 