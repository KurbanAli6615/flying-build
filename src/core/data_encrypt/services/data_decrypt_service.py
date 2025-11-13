import base64
import json
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as crypto_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fastapi import Request

from core.common_helpers import decrypt
from core.data_encrypt.schemas import EncryptedRequest


class DataEncryptService:
    """
    Service providing methods for data operations.
    """

    def __init__(self) -> None:
        pass

    async def decrypt_data_admin(
        self, request: Request, encrypted_request: EncryptedRequest
    ):
        """
        Decrypt data using RSA and AES.
        """
        decrypted_data = await decrypt(
            rsa_key=request.app.state.rsa_key,
            enc_data=encrypted_request.encrypted_data,
            encrypt_key=encrypted_request.encrypted_key,
            iv_input=encrypted_request.iv,
        )
        decrypted_data = json.loads(decrypted_data)
        return decrypted_data

    def load_public_key(self, public_key_path: str = "public_key.pem"):
        """
        Load RSA public key from PEM file.

        :param public_key_path: Path to the public key file
        :return: RSA public key object
        """
        with open(public_key_path, "rb") as key_file:
            public_key_data = key_file.read()

        public_key = serialization.load_pem_public_key(
            public_key_data, backend=default_backend()
        )
        return public_key

    def generate_aes_key_and_iv(self):
        """
         Generate a random 32-byte AES key and 16-byte IV.

        The AES key is generated as a 32-character ASCII string so that
        when UTF-8 encoded it produces exactly 32 bytes for AES-256.

           :return: Tuple of (AES key string, IV bytes)
        """
        # Generate 32 random ASCII printable characters for AES key
        # This ensures when UTF-8 encoded it's exactly 32 bytes
        # Ensure all characters are printable ASCII (32-126)
        aes_key_str = "".join(chr((c % 95) + 32) for c in os.urandom(32))
        iv = os.urandom(16)  # 16 bytes for IV
        return aes_key_str, iv

    def encrypt_data_with_aes(self, data: dict, aes_key: str, iv: bytes) -> bytes:
        """
        Encrypt data using AES-CBC with PKCS7 padding.

        :param data: Dictionary data to encrypt
        :param aes_key: 32-character ASCII string (32 bytes when UTF-8 encoded)
        :param iv: 16-byte initialization vector
        :return: Encrypted data as bytes
        """
        # Convert data to JSON string, then to bytes
        data_json = json.dumps(data)
        data_bytes = data_json.encode("utf-8")

        # Add PKCS7 padding
        padder = crypto_padding.PKCS7(128).padder()
        padded_data = padder.update(data_bytes) + padder.finalize()

        # Encrypt with AES-CBC using UTF-8 encoded key
        cipher = Cipher(
            algorithms.AES(aes_key.encode("utf-8")),
            modes.CBC(iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        return encrypted_data

    def encrypt_aes_key_with_rsa(
        self, aes_key: str, public_key: rsa.RSAPublicKey
    ) -> bytes:
        """
        Encrypt AES key using RSA public key with PKCS1v15 padding.

        The AES key is a 32-character string that when UTF-8 encoded
        produces exactly 32 bytes for AES-256.

        :param aes_key: 32-character ASCII string (32 bytes when UTF-8 encoded)
        :param public_key: RSA public key object
        :return: Encrypted AES key as bytes
        """
        # Encrypt the key string directly
        # When decrypted, it will be the same string, and when UTF-8 encoded
        # it will produce the 32 bytes needed for AES
        encrypted_key = public_key.encrypt(
            aes_key.encode("utf-8"), asym_padding.PKCS1v15()
        )
        return encrypted_key

    def encrypt_data(self, data: dict, public_key_path: str = "public_key.pem"):
        """
        Main encryption function that encrypts data using hybrid encryption:
        - AES-CBC for data encryption
        - RSA for AES key encryption

        :param data: Dictionary data to encrypt
        :param public_key_path: Path to the RSA public key file
        :return: Tuple of (encrypted_data, encrypted_key, iv) all as base64 strings
        """
        # Load public key
        public_key = self.load_public_key(public_key_path)

        # Generate AES key (32 bytes) and IV (16 bytes)
        aes_key, iv = self.generate_aes_key_and_iv()

        # Encrypt data with AES
        encrypted_data = self.encrypt_data_with_aes(data, aes_key, iv)

        # Encrypt AES key with RSA
        encrypted_key = self.encrypt_aes_key_with_rsa(aes_key, public_key)

        # Base64 encode everything
        encrypted_data_b64 = base64.b64encode(encrypted_data).decode("utf-8")
        encrypted_key_b64 = base64.b64encode(encrypted_key).decode("utf-8")
        iv_b64 = base64.b64encode(iv).decode("utf-8")

        return encrypted_data_b64, encrypted_key_b64, iv_b64
