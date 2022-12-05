import os, uuid, base64
from datetime import datetime
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256

from ..config import Config

class User:
    """
        This class represent an user object
            - userid
            - username
            - password_crypt
            - salt
            - created_at
            - lastmodified_at
    """
    def __init__(
        self, 
        username: str, 
        password: str = None, 
        password_crypt: str = None,
        salt: str = None, 
        created_at = None,
        lastmodified_at = None,
        user_id: str = None
    ):
        self.username = username
        self.id = user_id if user_id is not None else uuid.uuid4().hex
        self.created_at = self.__processDateTime(created_at)
        self.lastmodified_at = self.__processDateTime(lastmodified_at)        
        self.salt = salt if salt is not None else base64.b64encode(os.urandom(16)).decode(Config.BYTES_ENCODING)
        assert password is None or password_crypt is None, "Only one of password or password crypt must be provided"
        assert password is not None or password_crypt is not None, "Only one of password or password crypt must be provided"
        self.password_crypt = password_crypt if password_crypt is not None else self.create_password_crypt(password, self.salt)

    def __processDateTime(self, ts):
        if ts is None:
            return datetime.now().timestamp()
        elif isinstance(ts, datetime):
            return ts.timestamp()
        else:
            return float(ts)

    def create_password_crypt(self, password: str, salt: str):
        kdf = Scrypt(salt.encode(Config.BYTES_ENCODING), 32, n = 2**14, r = 8, p = 1)
        cryptbytes = kdf.derive(password.encode(Config.BYTES_ENCODING))
        return base64.b64encode(cryptbytes).decode(Config.BYTES_ENCODING)

    def verify_password_crypt(self, password: str):
        kdf = Scrypt(self.salt.encode(Config.BYTES_ENCODING), 32, n = 2**14, r = 8, p = 1)
        try:
            crypt64bytes = self.password_crypt.encode(Config.BYTES_ENCODING)
            kdf.verify(password.encode(Config.BYTES_ENCODING), base64.b64decode(crypt64bytes))
            return True
        except Exception as e:
            return False

    def generateMasterKey(self, password: str):
        if self.verify_password_crypt(password):
            saltbytes = base64.b64decode(self.salt.encode(Config.BYTES_ENCODING))
            kdf = PBKDF2HMAC(algorithm=SHA256(),length=32, salt=saltbytes,iterations=390000)
            return base64.urlsafe_b64encode(kdf.derive(password.encode(Config.BYTES_ENCODING)))
        else:
            raise PermissionError("Incorrect password, cannot generate master key")