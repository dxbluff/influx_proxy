from pyope.ope import OPE

from .serialize import *

OPE_KEY_FILE = "ope_key.txt"


# Some helpers for OPE cipher
def generate_key():
    random_key = OPE.generate_key()
    save(OPE_KEY_FILE, random_key)
    return random_key


def get_key():
    key = load(OPE_KEY_FILE)
    if key == None:
        key = generate_key()
    return key


def get_ope_cipher():
    return OPE(get_key())


if __name__ == "__main__":
    cipher = get_cipher()
    cyphertext = cipher.encrypt(1000)
    print(str(cyphertext))
    plaintext = cipher.decrypt(cyphertext)
    print(str(plaintext))
