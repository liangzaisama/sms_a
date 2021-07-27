"""
用户相关工具类及函数
"""
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def aes_decrypt(key, data):
    """对密码进行解密

    登录时用户输入的密码会进行加密，这里负责对密码进行解密
    如果解密失败会抛出AES包中相关的异常信息

    Args:
        key: 解密密钥
        data: 要解密的字符串

    Returns:
        result: 解密后的结果
    """
    data = data.encode()
    encode_bytes = base64.decodebytes(data)
    cipher = AES.new(key.encode(), AES.MODE_CBC, key.encode())
    text_decrypted = cipher.decrypt(encode_bytes)
    unpad_password = unpad(text_decrypted, AES.block_size)

    return unpad_password.decode()
