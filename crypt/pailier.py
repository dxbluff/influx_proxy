import pickle

from paillier import paillier

from .serialize import *

PAILLIER_PUB_KEY = "paillier_pub.txt"
PAILLIER_PRIVATE_KEY = "paillier_priv.txt"


# Decorator for HE cipher. Easy to re-implement
class HECipher:
    def __init__(self, priv, pub):
        self.priv = priv
        self.pub = pub

    def encrypt(self, value):
        return paillier.encrypt(self.pub, value)

    def decrypt(self, value):
        return paillier.decrypt(self.priv, self.pub, value)


def generate_key():
    priv, pub = paillier.generate_keypair(128)
    save(PAILLIER_PUB_KEY, pickle.dumps(pub))
    save(PAILLIER_PRIVATE_KEY, pickle.dumps(priv))
    return priv, pub


def get_key():
    priv = load(PAILLIER_PRIVATE_KEY)
    if priv == None:
        return generate_key()
    pub = load(PAILLIER_PUB_KEY)
    if pub == None:
        return generate_key()
    return pickle.loads(priv), pickle.loads(pub)


def get_he_cipher():
    priv, pub = get_key()
    return HECipher(priv, pub)


if __name__ == '__main__':
    # kind of dummy test
    cipher = get_he_cipher()
    ct = cipher.encrypt(123)
    print(str(ct))
    pt = cipher.decrypt(ct)
    print(str(pt))
