from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import argparse

def encrypt_decrypt_file(input_file, output_file=None, operation='encrypt', password=None):
    """
    使用密码对文件进行加密或解密
    
    参数:
        input_file (str): 输入文件路径
        output_file (str, optional): 输出文件路径，默认为None（自动生成）
        operation (str): 'encrypt' 或 'decrypt'
        password (str): 加密/解密密码
    
    返回:
        bool: 操作是否成功
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 文件 '{input_file}' 不存在")
        return False
    
    # 如果没有指定密码，则提示输入
    if not password:
        import getpass
        password = getpass.getpass("请输入加密/解密密码: ")
    
    # 如果没有指定输出文件，根据操作类型自动生成
    if output_file is None:
        if operation == 'encrypt':
            output_file = f"{input_file}.enc"
        else:
            # 如果是.enc文件，去掉.enc后缀
            if input_file.endswith('.enc'):
                output_file = input_file[:-4]
            else:
                output_file = f"{input_file}.decrypted"
    
    try:
        if operation == 'encrypt':
            # 读取原始文件
            with open(input_file, 'rb') as f:
                plaintext = f.read()
            
            # 生成随机salt和iv
            salt = os.urandom(16)
            iv = os.urandom(16)
            
            # 从密码生成密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
            
            # 加密数据
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            # 添加PKCS7填充
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            
            # 执行加密
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # 写入加密文件 (格式: salt + iv + 加密数据)
            with open(output_file, 'wb') as f:
                f.write(salt + iv + ciphertext)
            
            print(f"文件已成功加密到: {output_file}")
            return True
            
        elif operation == 'decrypt':
            # 读取加密文件
            with open(input_file, 'rb') as f:
                data = f.read()
            
            # 提取salt, iv和加密数据
            salt = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]
            
            # 从密码生成密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
            
            # 解密数据
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 去除填充
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            # 写入解密文件
            with open(output_file, 'wb') as f:
                f.write(plaintext)
            
            print(f"文件已成功解密到: {output_file}")
            return True
        
        else:
            print(f"错误: 不支持的操作 '{operation}'，请使用 'encrypt' 或 'decrypt'")
            return False
            
    except Exception as e:
        print(f"操作过程中发生错误: {str(e)}")
        return False


# 命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='使用密码加密或解密文件')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    parser.add_argument('-op', '--operation', choices=['encrypt', 'decrypt'], 
                        required=True, help='执行的操作: encrypt（加密）或 decrypt（解密）')
    parser.add_argument('-p', '--password', help='加密/解密密码')
    
    args = parser.parse_args()
    
    encrypt_decrypt_file(
        args.input, 
        args.output, 
        args.operation, 
        args.password
    )