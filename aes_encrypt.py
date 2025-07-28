from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import time


def aes_crypt(pid, uuid, sn, random_num, key):
    plaintext = f"{pid}|||{uuid}|||{sn}|||{random_num}"
    plaintext_bytes = plaintext.encode('utf-8')

    padded_data = pad(plaintext_bytes, AES.block_size)
    # print(padded_data)

    key = key[:16].encode('utf-8')

    iv = b'\x00' * 16

    cipher = AES.new(key, AES.MODE_CBC, iv)
    # cipher = AES.new(key, AES.MODE_ECB)

    ciphertext = cipher.encrypt(padded_data)

    encoded = base64.b64encode(ciphertext).decode('utf-8')

    return encoded


random = str(int(time.time()))
encrypt_data = aes_crypt("co36zjpraqsta5si", "lzgd5496a7907243e22d", "C2E2DA110017952", random, "qyHZ93tFQn8gyrUTh4MkyN5O09Qc4HkK")
print(encrypt_data)
print(random)
