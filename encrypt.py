from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

# Generate random KEY, JUST FOR EXAMPLE, it should be generating and writing in .env
KEY = os.urandom(32)  # 256 bit


def encrypt_user_id(user_id: str, key: bytes) -> str:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(user_id.encode('utf-8')) + encryptor.finalize()
    return base64.urlsafe_b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_user_id(encoded_data: str, key: bytes) -> str:
    combined_data = base64.urlsafe_b64decode(encoded_data)
    iv = combined_data[:16]
    encrypted_data = combined_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data.decode('utf-8')


user_id = "123456"
ref_code = "654321"
src_data = user_id + ref_code
encrypted_code = encrypt_user_id(src_data, KEY)
print("Encrypted referral code:", encrypted_code)

decrypted_dest_data = decrypt_user_id(encrypted_code, KEY)
print("Decrypted dest_data:", decrypted_dest_data)