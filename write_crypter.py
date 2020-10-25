from base64 import b64encode, b64decode
from pathlib import Path

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor, Node

from crypt.aes import get_cipher
from crypt.ope import get_ope_cipher
from crypt.pailier import get_he_cipher

root = Path(__file__).parent
grammars = root / "grammars"


def base64padder(string):
    missing_padding = len(string) % 4
    if missing_padding:
        string += '=' * (4 - missing_padding)
    return string


he_cipher = get_he_cipher()
ope_cipher = get_ope_cipher()
det_cipher = get_cipher()


def det_encrypt_string(s):
    ct = get_cipher().encrypt(s.encode())
    return b64encode(ct).decode().replace("=", "")


def det_decrypt_string(s):
    s = base64padder(s)
    ct = b64decode(s.encode())
    pt = get_cipher().decrypt(ct.decode())
    return pt.decode()


def ope_encrypt_int(value):
    return ope_cipher.encrypt(value)


def ope_decrypt_int(value):
    return ope_cipher.decrypt(value)


def he_encrypt(value):
    return he_cipher.encrypt(value)


def he_decrypt(value):
    return he_cipher.decrypt(value)


class WriteEncrypter(NodeVisitor):

    def _det_encrypt(self, node: Node, visited_children):
        token = node.text
        encrypted = det_encrypt_string(token)
        return encrypted

    def _encrypt_field(self, node: Node, visited_children):
        field_key, field_value = node.text.split("=")
        encrypted_field_key_phe = f'phe_{det_encrypt_string(field_key)}'
        encrypted_field_key_ope = f'ope_{det_encrypt_string(field_key)}'

        encrypted_field_value_phe = he_encrypt(int(field_value))
        encrypted_field_value_ope = ope_encrypt_int(int(field_value))

        new_field = f"{encrypted_field_key_phe}={encrypted_field_value_phe},{encrypted_field_key_ope}={encrypted_field_value_ope}"
        return new_field

    visit_measurement = _det_encrypt
    visit_tag_key = _det_encrypt
    visit_tag_value = _det_encrypt
    visit_field = _encrypt_field

    def generic_visit(self, node, visited_children):
        return ''.join(visited_children) or node.text  # Для неопределенных токенов возвращаем просто их текст


class WriteDecrypter(NodeVisitor):

    def _det_decrypt(self, node: Node, visited_children):
        token = node.text
        return det_decrypt_string(token)

    def _decrypt_field(self, node: Node, visited_children):
        field_key, field_value = node.text.split('=')

        if field_key[:4] == "phe_":
            decrypted_field_key_phe = det_decrypt_string(field_key.replace("phe_", ''))
            decrypted_field_value_phe = he_decrypt(int(field_value))
            return f"{decrypted_field_key_phe}={decrypted_field_value_phe}"

        if field_key[:4] == "ope_":
            decrypted_field_key_ope = det_decrypt_string(field_key.replace("ope_", ''))
            decrypted_field_value_ope = ope_decrypt_int(int(field_value))
            return f"{decrypted_field_key_ope}={decrypted_field_value_ope}"

        return node.text

    visit_measurement = _det_decrypt
    visit_tag_key = _det_decrypt
    visit_tag_value = _det_decrypt
    visit_field = _decrypt_field

    def generic_visit(self, node, visited_children):
        return ''.join(visited_children) or node.text  # Для неопределенных токенов возвращаем просто их текст


class QueryEncrypter(NodeVisitor):

    def _det_encrypt(self, node: Node, visited_children):
        token = node.text.replace('"', '')
        encrypted = det_encrypt_string(token)
        return encrypted

    visit_identifier = _det_encrypt

    def generic_visit(self, node, visited_children):
        return ''.join(visited_children) or node.text  # Для неопределенных токенов возвращаем просто их текст


with (grammars / 'write.grammar').open(mode='r', encoding='utf-8') as fp:
    write_grammar = Grammar(fp.read())

with (grammars / 'influxql.grammar').open(mode='r', encoding='utf-8') as fp:
    influxql = Grammar(fp.read())


def encrypt_write_query(query):
    tree_plain = write_grammar.parse(query)
    write_encrypter = WriteEncrypter()
    encrypted_query = write_encrypter.visit(tree_plain)
    return encrypted_query


def decrypt_write_query(encrypted_payload):
    tree_encrypted = write_grammar.parse(encrypted_payload)
    write_decrypter = WriteDecrypter()
    decrypted_payload = write_decrypter.visit(tree_encrypted)
    return decrypted_payload


def encrypt_query(query):
    tree_plain = influxql.parse(query)
    query_encrypter = QueryEncrypter()
    encrypted_query = query_encrypter.visit(tree_plain)
    return encrypted_query


def main():
    write_payload = "weather,location=us-midwest temperature=82 1465839830100400200"
    print(f"\nPlain payload: \n{write_payload}\n")
    encrypted_payload = encrypt_write_query(write_payload)
    print(f"\nEncrypted payload: \n{encrypted_payload}\n")
    decrypted_payload = decrypt_write_query(encrypted_payload)
    print(f"\nDecrypted payload: \n{decrypted_payload}\n")

    select_payload = 'SELECT * FROM "weather"'
    encrypted_select_query = encypt_query(select_payload)
    print(f"\nEncrypted select payload: \n{encrypted_select_query}\n")


if __name__ == "__main__":
    main()
