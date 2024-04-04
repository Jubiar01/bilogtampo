import base64
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from datetime import datetime

configKeys = [
        "662ede816988e58fb6d057d9d85605e0",  # Key 1
        "162exe235948e37ws6d057d9d85324e2",  # Key 2
        "962exe865948e37ws6d057d4d85604e0",  # Key 3
        "175exe868648e37wb9x157d4l45604l0",  # Key 4
        "175exe867948e37wb9d057d4k45604l0"   # Key 5
    ]

def decrypt_sks_file(encryptedContents):
    try:
        configFile = json.loads(encryptedContents)
        parts = configFile["d"].split(".")
        iv = base64.b64decode(parts[1])
        data = base64.b64decode(parts[0])

        key = md5crypt(configKeys[1] + " " + str(configFile["v"]))
        secretKeySpec = AES.new(key.encode(), AES.MODE_CBC, iv)

        decryptedBytes = unpad(secretKeySpec.decrypt(data), AES.block_size)
        decryptedData = decryptedBytes.decode('utf-8')

        return formatConfig(json.loads(decryptedData))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Decryption failed: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def formatConfig(data):
    if not data:
        return "No configuration data provided."

    lines = ["============== Configuration =============="]

    for section, details in data.items():
        lines.append(f"[{section}]")
        if isinstance(details, dict):
            _format_dict_details(details, lines, prefix="")
        else:
            lines.append(f"{section}: {details}")

    lines.append("\n============== Configuration ==============")
    lines.append("Made By - Biar")

    return "\n".join(lines)

def _format_dict_details(details, lines, prefix=""):
    for key, value in details.items():
        if isinstance(value, dict):
            _format_dict_details(value, lines, prefix=f"{prefix}[</>]{key}")
        else:
            lines.append(f"{prefix}[</>]{key}: {value}")

def md5crypt(data):
    return hashlib.md5(data.encode()).hexdigest()
