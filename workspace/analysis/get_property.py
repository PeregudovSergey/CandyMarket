import sqlite3
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from add_idx_public_key import add_id
#items + volume + rank
def get_propery():
  add_id()
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    WITH tmp (public_key, volume) as (
    SELECT public_key, MIN(volume) + COALESCE(SUM(price),0) as volume
    FROM client LEFT JOIN shop 
    ON public_key = owner_public_key
    GROUP BY public_key
    ORDER BY volume DESC
    ) 
    SELECT idx, volume
    FROM tmp LEFT JOIN idx_public_key ON tmp.public_key=idx_public_key.public_key
    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df

data = get_propery().head()
fig = plt.figure(figsize = (10, 5))
plt.bar(data["idx"], list(data["volume"]), width = 0.4)
plt.grid(True)
plt.show()