import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

key = b"a"*32


def encrypt(data: bytes | str) -> bytes:
    payload_bytes = data.encode() if isinstance(data, str) else data

    # Preenche até completar o bloco de 16 bytes do AES apenas se não for múltiplo
    if len(payload_bytes) % 16 != 0:
        padder = padding.PKCS7(128).padder()
        payload_bytes = padder.update(payload_bytes) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    return encryptor.update(payload_bytes) + encryptor.finalize()


def decrypt(data: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data) + decryptor.finalize()

    try:
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(decrypted_data) + unpadder.finalize()
    except Exception:
        return decrypted_data