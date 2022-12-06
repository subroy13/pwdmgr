import os, uuid, base64
from datetime import datetime
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256

from ..config import Config

class User:
    """
        This class represents an user object in database
    """
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1


    def __init__(
        self,
        username: str,
        useremail: str,
        password: str = None
    ):
        # creates a new user object
        self.username = username
        self.useremail = useremail
        self.id = uuid.uuid4().hex
        self.created_at = datetime.now().timestamp()
        self.lastmodified_at = self.created_at
        self.salt = base64.b64encode(os.urandom(16)).decode(Config.BYTES_ENCODING)
        if password is not None:
            self.password = self.create_password_crypt(password, self.salt)
        else:
            self.password = None
        self.status = User.STATUS_ACTIVE


    @classmethod
    def convertToUser(cls, dbuser):
        # convert the user saved in db to a proper user object
        user = User(
            dbuser['username'],
            dbuser['useremail'],
            None
        )
        user.created_at = cls.__processDateTime(dbuser['createdat'])
        user.lastmodified_at = cls.__processDateTime(dbuser['lastmodifiedat'])
        user.id = dbuser['userid']
        user.password = dbuser['password']
        user.salt = dbuser['salt']
        user.status = dbuser['status']
        assert user.status in [User.STATUS_ACTIVE, User.STATUS_INACTIVE]
        return user

    @classmethod
    def __processDateTime(cls, ts):
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
