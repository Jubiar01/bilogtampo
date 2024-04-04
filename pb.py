import base64
import re
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

def decrypt_pb_file(file_content):
    # Split the encrypted content into salt, nonce, and cipher
    encrypted_components = file_content.split(b'.')
    salt = base64.b64decode(encrypted_components[0].strip())
    nonce = base64.b64decode(encrypted_components[1].strip())
    ciphertext = base64.b64decode(encrypted_components[2].strip())
    
    # Derive the key using Cw1G6s0K8fJVKZmhSLZLw3L1R3ncNJ2e
    config_enc_password = "Cw1G6s0K8fJVKZmhSLZLw3L1R3ncNJ2e"
    key = PBKDF2(config_enc_password.encode('utf-8'), salt, dkLen=16, count=1000, prf=lambda p, s: hmac.new(p, s, hashlib.sha256).digest())
    
    # Decrypt the ciphertext using AES-GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext[:-16], ciphertext[-16:])
    
    # Remove padding from decrypted data
    unpadded_data = remove_padding(decrypted_data)
    
    # Extract entries using regex pattern
    pattern = re.compile(rb'<entry key="(.*?)">(.*?)</entry>')
    matches = pattern.findall(unpadded_data)

    # Build the result string
    result_builder = []
    for match in matches:
        key_str = match[0].decode('utf-8')
        value_str = match[1].decode('utf-8')
        result_builder.append(f"[</>] [{key_str}]= {value_str}\n")
    result_builder.append("\n\nMade By BiarZ")

    return ''.join(result_builder)

def remove_padding(decrypted_text):
    padding_length = decrypted_text[-1]
    return decrypted_text[:-padding_length]

# Example usage:
# encrypted_content = read_file('path_to_your_encrypted_file.tnl')
# decrypted_content = decrypt_tnl_file(encrypted_content)
# print(decrypted_content)
