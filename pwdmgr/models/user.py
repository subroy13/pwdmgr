import os, uuid, base64, pyotp
from datetime import datetime
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.fernet import Fernet

BYTES_ENCODING = os.getenv("APP_BYTES_ENCODING")
APP_SECRET = os.getenv("APP_SECRET")

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
        self.salt = base64.b64encode(os.urandom(16)).decode(BYTES_ENCODING)
        if password is not None:
            self.password = self.create_password_crypt(password, self.salt)
        else:
            self.password = None
        self.qr_seed = self.encrypt_totp_seed(pyotp.random_base32(), password)
        self.status = User.STATUS_ACTIVE

    def serialize(self):
        return {
            "userid": self.id,
            "username": self.username,
            "useremail": self.useremail,
            "status": self.status
        }


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
        user.qr_seed = dbuser['qrseed']
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

    def encrypt_totp_seed(self, seed: str, password: str):
        master_key = self.generateMasterKey(password, APP_SECRET)
        f = Fernet(master_key)
        return f.encrypt(seed.encode(BYTES_ENCODING)).decode(BYTES_ENCODING)

    def decrypt_totp_seed(self, encrypted_seed:str, password: str):
        master_key = self.generateMasterKey(password, APP_SECRET)
        f = Fernet(master_key)
        return f.decrypt(encrypted_seed.encode(BYTES_ENCODING)).decode(BYTES_ENCODING)

    def create_password_crypt(self, password: str, salt: str):
        kdf = Scrypt(salt.encode(BYTES_ENCODING), 32, n = 2**14, r = 8, p = 1)
        cryptbytes = kdf.derive(password.encode(BYTES_ENCODING))
        return base64.b64encode(cryptbytes).decode(BYTES_ENCODING)

    def verify_password_crypt(self, password: str):
        kdf = Scrypt(self.salt.encode(BYTES_ENCODING), 32, n = 2**14, r = 8, p = 1)
        try:
            crypt64bytes = self.password.encode(BYTES_ENCODING)
            kdf.verify(password.encode(BYTES_ENCODING), base64.b64decode(crypt64bytes))
            return True
        except Exception as e:
            return False

    def generateMasterKey(self, password: str, extrapart : str = None):
        if self.verify_password_crypt(password):
            saltbytes = base64.b64decode(self.salt.encode(BYTES_ENCODING))
            kdf = PBKDF2HMAC(algorithm=SHA256(),length=32, salt=saltbytes,iterations=390000)
            if extrapart is None:
                return base64.urlsafe_b64encode(kdf.derive(password.encode(BYTES_ENCODING)))
            else:
                return base64.urlsafe_b64encode(kdf.derive((password + extrapart).encode(BYTES_ENCODING)))
        else:
            raise PermissionError("Incorrect password, cannot generate master key")