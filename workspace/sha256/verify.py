#!/usr/bin/env python

import sys

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import time
time.clock = time.time


def verify(message, public_key, sig):
    # message = "I want this stream signed"
    digest = SHA256.new()
    digest.update(message.encode('utf-8'))
    sig = bytes.fromhex(sig)  # convert string to bytes object

    # Load public key (not private key) and verify signature
    public_key = RSA.importKey(public_key)
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, sig)

    return verified
