import sqlite3
import time
import hashlib
from random import randint
import xmlrpc.server
import sys
sys.path.insert(0, '../sha256')
from verify import verify

cur_id_item = 0
gas_limit = 0.3
current_block = 0 #index of current block
current_reward = 128 #reward for block
shop_public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDTWzlAvOnRMyWpzfDgxkoty4tZ
0YOqJ1wDJNM6LPAHBDsFZn2JlFjrqgzmJIxZ1fxWmRrTJwmss0PTF5pCeyeitkiX
FFBRzKj6bwgHDp5vPSrLzd2Szk/Zr7sZm4nPPGWJbjnM0wdR+j/Rqh6LnmSYQwlT
eapA+qr/8Cb9cQVCuQIDAQAB
-----END PUBLIC KEY-----""" #shop public key
percent_shop_tax = 0.001 #tax for every single tx
difficulty_of_mining = 1 #difficulty of puzzle: number of zeroes for sha256
limit_on_number_of_tx = 10 #miner can pack for a maximum of 10 tx in single block
hash_last_block = ""

def register_wallet(public_key):
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  info = cursor.execute("""
    SELECT * 
    FROM client 
    WHERE public_key=?
  """, (public_key, )).fetchone()
  if info == None:
    cursor.execute('INSERT INTO client VALUES (?, 0)', (public_key, ))
  connection.commit()
  connection.close()

def get_current_block():
  return current_block

def check_sign(pk_sender, sig):
  secret = pk_sender + str(current_block)
  return verify(secret, pk_sender, sig)

def get_balance(public_key):
  register_wallet(public_key)
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  row = cursor.execute("""
    SELECT volume
    FROM client 
    WHERE public_key=?
  """, (public_key, )).fetchone()
  connection.commit()
  connection.close()
  return row[0]

def set_balance(public_key, new_balance):
  register_wallet(public_key)
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    UPDATE client
    SET volume=?
    WHERE public_key=?
  """, (new_balance, public_key, ))
  connection.commit()
  connection.close()

def add_balance(public_key, add):
  cur_bal = get_balance(public_key) + add
  set_balance(public_key, cur_bal)

def record_available_net_tx(pk_sender, pk_receiver, value, gas):
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    INSERT INTO available_net_tx VALUES (?, ?, ?, ?)
  """, (pk_sender, pk_receiver, value, gas, ))
  connection.commit()
  connection.close()

def delete_available_net_tx(pk_sender, pk_receiver, value, gas):
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    DELETE FROM available_net_tx 
    WHERE sender=? and receiver=? and value=? and gas=?;
  """, (pk_sender, pk_receiver, value, gas, ))
  connection.commit()
  connection.close()

#user send tx to net
def add_tx(pk_sender, pk_receiver, value, gas, sig):
  if gas < gas_limit:
    return -1
  if not check_sign(pk_sender, sig):
    return -1
  register_wallet(pk_sender)
  register_wallet(pk_receiver)
  sender_balance = get_balance(pk_sender)
  receiver_balance = get_balance(pk_receiver)
  if sender_balance < gas + value:
    return -1
  #spend all output, waiting for miner
  set_balance(pk_sender, 0)
  available_tx.append([pk_sender, pk_sender, sender_balance - value - gas, gas / 2])
  record_available_net_tx(pk_sender, pk_sender, sender_balance - value - gas, gas / 2)
  available_tx.append([pk_sender, pk_receiver, value, gas / 2]) 
  record_available_net_tx(pk_sender, pk_receiver, value, gas / 2)
  return 1

def record_to_blockhain(pk_sender, pk_receiver, value, gas, block):
  register_wallet(pk_sender)
  register_wallet(pk_receiver)

  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    INSERT INTO blockchain VALUES (?, ?, ?, ?, ?)
  """, (pk_sender, pk_receiver, value, gas, block, ))
  connection.commit()
  connection.close()

def get_list_tx():
  return available_tx

def check_tx_availible(list_of_tx):
  for tx in list_of_tx:
    if not tx in available_tx:
      return False
  return True
  

def build_miner_string(list_of_tx, hash):
  secret = hash_last_block
  for element in list_of_tx:
    for x in element:
      secret += str(x)
  secret += str(hash)
  return secret

#check sha is correct
def ends_with_zeroes(sha256_code):
  for i in range(difficulty_of_mining):
    if sha256_code[i] != '0':
      return False
  return True

def record_block_info(block, pk_miner, reward, hash, date):
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    INSERT INTO block_info VALUES (?, ?, ?, ?, ?)
  """, (block, pk_miner, reward, hash, date, ))
  connection.commit()
  connection.close()

#miner send packed tx
def miner_packed_tx(list_of_tx, hash, pk_miner):
  global current_block, limit_on_number_of_tx, current_reward, shop_public_key
  if len(list_of_tx) > limit_on_number_of_tx:
    return -1
  if not check_tx_availible(list_of_tx):
    return -1
  secret = build_miner_string(list_of_tx, hash) #check that miner is right
  sha256_code = hashlib.sha256(secret.encode('utf-8')).hexdigest() #check that miner is right
  if not ends_with_zeroes(sha256_code):
    return -1
  tax = 0 #sum of tax of tx
  for tx in list_of_tx:
    tax += tx[3]
  add_balance(shop_public_key, tax * percent_shop_tax) #take tax for usage server
  add_balance(pk_miner, tax * (1 - percent_shop_tax) + current_reward) #give reward + remain tax for tx to miner
  
  for tx in list_of_tx:
    add_balance(tx[1], tx[2]) #send token
  for tx in list_of_tx:
    available_tx.remove(tx)
    delete_available_net_tx(tx[0], tx[1], tx[2], tx[3])
    record_to_blockhain(tx[0], tx[1], tx[2], tx[3], current_block)
  record_block_info(current_block, pk_miner, current_reward, hash, time.time())
  current_block += 1
  return 1

def record_to_item_description(id_item, item_description): 
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    INSERT INTO item_description VALUES (?, ?)
  """, (id_item, item_description, ))
  connection.commit()
  connection.close()

#shop register item
def register_item(item_description, sig):
  global shop_public_key
  if not check_sign(shop_public_key, sig):
    return -1
  round_vote = []
  record_to_item_description(cur_id_item, item_description)

def record_vote(pk, fair_price):
  global current_block
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    INSERT INTO vote VALUES (?, ?, ?)
  """, (pk, fair_price, current_block, ))
  connection.commit()
  connection.close()

#people vote for the product
def vote_for_item(price, id_item, sig, pk):
  if not check_sign(pk, sig):
    return -1
  if id_item != cur_id_item:
    return -1
  for x in round_vote:
    if x[2] == pk:
      return -1

  round_vote.append([get_balance(pk), price, pk])
  record_vote(pk, price)
  
def record_item_to_shop(id_item, price):
  global shop_public_key
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute("""
    INSERT INTO shop VALUES (?, ?, ?)
  """, (id_item, shop_public_key, price, ))
  connection.commit()
  connection.close()

#shop ends voting 
def finish_vote(sig):
  global shop_public_key
  if not check_sign(shop_public_key, sig):
    return -1
  sum = 0
  for x in round_vote:
    sum += x[0]
  fair_price = 0
  for x in round_vote:
    fair_price += x[0] / sum * x[1]
  record_item_to_shop(cur_id_item, fair_price)
  cur_id_item += 1

#description of item
def get_description(id_item):
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  row = cursor.execute("""
    SELECT volume
    FROM shop 
    WHERE id_item=?
  """, (id_item, )).fetchone()
  connection.commit()
  connection.close()
  if row == None:
    return -1
  return row[1]

available_tx = []
connection = sqlite3.connect('../concurrency.db')
cursor = connection.cursor()
info = cursor.execute("""
    SELECT *
    FROM available_net_tx 
  """).fetchall()
for x in info: 
  available_tx.append([x[0], x[1], x[2], x[3]])
connection.close()

round_vote = []
server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
#add tx + mine block
server.register_function(add_tx)
server.register_function(miner_packed_tx)
#user func
server.register_function(get_balance)
server.register_function(get_list_tx)
server.register_function(get_current_block)
server.register_function(get_description)

#miner func
server.register_function(build_miner_string)
server.register_function(ends_with_zeroes)
#add item to shop
server.register_function(register_item)
server.register_function(vote_for_item)
server.register_function(finish_vote)

server.serve_forever()