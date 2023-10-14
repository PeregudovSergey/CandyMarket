import sqlite3

#numerate public_key 
def add_id():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""DROP TABLE IF EXISTS idx_public_key;""")

  cursor.execute('''CREATE TABLE idx_public_key AS 
                    SELECT public_key, RANK() OVER (ORDER BY public_key) as idx
                    FROM client
                    
  ''')
  connection.commit()
  connection.close()