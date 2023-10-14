import sqlite3

connection = sqlite3.connect('concurrency.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS blockchain
              (sender text, receiver text, price numeric, gas numeric, id_block bigint)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS block_info
              (id_block bigint, miner text, reward numeric, hash bigint, date TIMESTAMP)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS available_net_tx
              (sender text, receiver text, value numeric, gas numeric)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS client
              (public_key text, volume numeric)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS shop
              (id_item bigint, owner_public_key text, price numeric)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS item_description
              (id_item bigint, description text)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS vote
              (public_key text, fair_price numeric, id_block bigint)''')

cursor.execute('''INSERT INTO client VALUES ('-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDTWzlAvOnRMyWpzfDgxkoty4tZ
0YOqJ1wDJNM6LPAHBDsFZn2JlFjrqgzmJIxZ1fxWmRrTJwmss0PTF5pCeyeitkiX
FFBRzKj6bwgHDp5vPSrLzd2Szk/Zr7sZm4nPPGWJbjnM0wdR+j/Rqh6LnmSYQwlT
eapA+qr/8Cb9cQVCuQIDAQAB
-----END PUBLIC KEY-----', 50000)''')
               
connection.commit()
connection.close()