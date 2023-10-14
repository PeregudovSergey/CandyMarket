import sqlite3

#add index by public key 
def add_index_client():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""CREATE UNIQUE INDEX public_key_fast ON client (public_key);""")

  connection.commit()
  connection.close()

def add_index_block_info():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""CREATE UNIQUE INDEX id_block_fast ON block_info (id_block);""")

  connection.commit()
  connection.close()

add_index_client()
add_index_block_info()