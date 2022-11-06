import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256

from ..config import Config

class User:
    """
        This class represent an user object
            - username
            - password_crypt
            - salt object randomly generated
    """
    def __init__(self, username: str, salt: str = None, password: str = None, password_crypt: str = None):
        self.__username = username
        if salt is None:
            self.__salt = os.urandom(16).decode(Config.BYTES_ENCODING)
        else:
            self.__salt = salt
        if password_crypt is None:
            assert password is not None, "Atleast one of password or password hash should be not null"
            self.__password_crypt = self.create_password_crypt(password, self.__salt)
        else:
            self.__password_crypt = password_crypt

    def create_password_crypt(self, password: str, salt: str):
        kdf = Scrypt(salt.encode(Config.BYTES_ENCODING), 32, n = 2**14, r = 8, p = 1)
        return kdf.derive(password.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)

    def verify_password_crypt(self, password: str):
        kdf = Scrypt(self.__salt.encode(Config.BYTES_ENCODING), 32, n = 2**14, r = 8, p = 1)
        try:
            kdf.verify(password.encode(Config.BYTES_ENCODING), self.__password_crypt.encode(Config.BYTES_ENCODING))
            return (True, self.__generateMasterKey(password))
        except Exception as e:
            return (False, None)

    def getData(self):
        return {
            "Username": self.__username,
            "Salt": self.__salt,
            "PasswordHash": self.__password_crypt 
        }

    def __generateMasterKey(self, password: str):
        kdf = PBKDF2HMAC(algorithm=SHA256(),length=32, salt=self.__salt,iterations=390000)
        key = kdf.derive(password.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        return key











