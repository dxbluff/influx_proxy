import json
from base64 import b64decode
from base64 import b64encode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from .serialize import *

AES_KEY_FILE = "aes_key.txt"


# Decorator for AES-SIV cipher. Easy to implement another here, just save contract
class DetCipher:
    def __init__(self, cipher):
        self.cipher = cipher

    def encrypt(self, data):
        c, t = self.cipher.encrypt_and_digest(data)
        return b64encode(c) + b";" + b64encode(t)

    def decrypt(self, string):
        splited_str = string.split(";")
        pt = self.cipher.decrypt_and_verify(b64decode(splited_str[0]), b64decode(splited_str[1]))
        return pt


def generate_key_info():
    key = get_random_bytes(16 * 2)
    nonce = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_SIV)
    encoded_key = b64encode(key).decode('utf-8')
    encoded_nonce = b64encode(nonce).decode('utf-8')
    key_info = json.dumps({'key': encoded_key, 'nonce': encoded_nonce}).encode()
    save(AES_KEY_FILE, key_info)
    return key_info


def get_key_info():
    key_info = load(AES_KEY_FILE)
    if (key_info == None):
        key_info = generate_key_info()
    return key_info


def get_cipher():
    key_info = get_key_info()
    b64 = json.loads(key_info)
    key = b64decode(b64['key'])
    nonce = b64decode(b64['nonce'])
    cipher = AES.new(key, AES.MODE_SIV, nonce=nonce)
    return DetCipher(cipher)


if __name__ == "__main__":
    cipher = get_cipher()
    data = b'lolkekcheburekkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
    ct = cipher.encrypt(data)
    print(ct)
    cipher = get_cipher()
    pt = cipher.decrypt(ct)
    print(data)
