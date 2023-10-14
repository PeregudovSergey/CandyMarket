#!/usr/bin/env python

#from base64 import (b64encode, b64decode)

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import time
time.clock = time.time


#message = "I want this stream signed"
def sign(message, private_key):
    digest = SHA256.new()
    digest.update(message.encode('utf-8'))

    # Load private key previouly generated
    private_key = RSA.importKey(private_key)

    # Sign the message
    signer = PKCS1_v1_5.new(private_key)
    sig = signer.sign(digest)

    # sig is bytes object, so convert to hex string.
    # (could convert using b64encode or any number of ways)
    return sig.hex()