import subprocess
import xmlrpc.server
import hashlib
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import sys
sys.path.insert(0, '../sha256')
from sign import sign

def process_key(key):
  key = ' '.join(key)
  return key

def get_sign(public_key, private_key):
   secret = public_key + str(server.get_current_block())
   return sign(secret, private_key)

shop_public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDTWzlAvOnRMyWpzfDgxkoty4tZ
0YOqJ1wDJNM6LPAHBDsFZn2JlFjrqgzmJIxZ1fxWmRrTJwmss0PTF5pCeyeitkiX
FFBRzKj6bwgHDp5vPSrLzd2Szk/Zr7sZm4nPPGWJbjnM0wdR+j/Rqh6LnmSYQwlT
eapA+qr/8Cb9cQVCuQIDAQAB
-----END PUBLIC KEY-----"""

shop_private_key = """-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBANNbOUC86dEzJanN
8ODGSi3Li1nRg6onXAMk0zos8AcEOwVmfYmUWOuqDOYkjFnV/FaZGtMnCayzQ9MX
mkJ7J6K2SJcUUFHMqPpvCAcOnm89KsvN3ZLOT9mvuxmbic88ZYluOczTB1H6P9Gq
HoueZJhDCVN5qkD6qv/wJv1xBUK5AgMBAAECgYAvHf0Lc5HkczSIQELcuRe8Uc4E
/fIOMqwOf10fcPkpd0X5FDoUO5//GW+6tpcbR9rzKzqRq/g6KdSK8I4RGAdjlOxJ
VuHeXxNnAz2tVmJltLWNwMvApMOxoY62SrpTX0m/h4g9Vas2+ALkG1GGK9fV91AC
kWzg0YrYjslinYOBoQJBAOqKOhIhQoeKJjbgDImkJNQrLKfDtB8DG1AUv+X8GVZo
RmlnroKnTnIQ/HH2QHilBqtKa5Kekt2h1vmnCrGGFn0CQQDmsfP1r9OAqjwChqie
kJhLbxcQoKAw/leZ7DtV3wwLZa4XpMprR5OdCXA3rFmhxUjJBMljf5FnlM+AMMsP
2gXtAkEAm8otQJWvJ3DwaUrxiQvrGrOC+fzYzDC4F71wqkeGXQruml0wYcDYLpRx
2xEDSh/0Chto0P9b9rPlo/b892Zl0QJBANHISRzGAwMhyuhRI8ztmFAgeUz5hDKJ
V4f1Ng/kgMNsd1+wzxG3SRiomI9H/0oIaSPDYo9EVilnPTpJJJ8JmBECQF9ty2nW
a6vrzKZFZ1E91F2TOGX1ewRbya9boa6qVuM4NmCnF0YaN+HbifPrw49fwxUd/8V8
QwNPf79sznRDC/g=
-----END PRIVATE KEY-----"""
server = xmlrpc.client.ServerProxy("http://localhost:8000")

def mine(public_key):
  list_of_tx = server.get_list_tx()
  hash = 0
  while True:
    secret = server.build_miner_string(list_of_tx, hash)
    sha256_code = hashlib.sha256(secret.encode('utf-8')).hexdigest() #check that miner is right
    if server.ends_with_zeroes(sha256_code):
       server.miner_packed_tx(list_of_tx, hash, public_key)
       break
    hash += 1

f = open("friends.txt", "w")
f.close()

for it in range(20):
  subprocess.call(['bash', '../sha256/generate_key.sh'])
  with open("private_key.pem", "r") as src:
      private_key = src.readlines()
      private_key = process_key(private_key)
  private_key1 = RSA.importKey(private_key)
  public_key = private_key1.publickey()
  public_key = public_key.exportKey().decode('utf-8')
  f = open("friends.txt", "a")
  f.write(public_key + '\n')
  f.write(private_key)
  f.write('\n\n')
  f.close()
  result = server.add_tx(shop_public_key, public_key, 1000, 1, get_sign(shop_public_key, shop_private_key))
  if result == -1:
     break
  mine(public_key)