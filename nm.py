import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import b64decode

def decrypt_message(key, encrypted_message):
    key = b64decode(key)
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return decrypted_message

def format_json(key, value, prefix="[</>] "):
    formatted_lines = []
    
    if isinstance(value, dict):
        if key:
            formatted_lines.append(f"{prefix}[{key}]:")
        for sub_key, sub_value in value.items():
            formatted_lines.extend(format_json(sub_key, sub_value, prefix))
    elif isinstance(value, list):
        formatted_lines.append(f"{prefix}[{key}]:")
        for item in value:
            formatted_lines.extend(format_json("", item, prefix))
    else:
        formatted_line = f"{prefix}[{key}]: {value}"
        formatted_lines.append(formatted_line)

    return formatted_lines

def decrypt_nm_file(file_content):
    key = "X25ldHN5bmFfbmV0bW9kXw=="
    encrypted_message = b64decode(file_content)
    decrypted_message = decrypt_message(key, encrypted_message).decode('utf-8')

    # Attempt to find the end of the JSON object and trim the extra data
    try:
        end_json_index = decrypted_message.rindex('}') + 1
        json_part = decrypted_message[:end_json_index]
        json_data = json.loads(json_part)
    except ValueError as e:
        print(f"Error finding valid JSON in decrypted message: {e}")
        return "Error: Decrypted data is not valid JSON"

    # Build the formatted output
    formatted_lines = ["==============================="]
    for key, value in json_data.items():
        formatted_lines.extend(format_json(key, value))
    formatted_lines.append("===============================")

    formatted_output = "\n".join(formatted_lines)

    return formatted_output
