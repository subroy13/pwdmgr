import json, uuid, base64
from datetime import datetime 
from cryptography.fernet import Fernet

from ..config import Config
from .user import User
from ..api.userapi import getUserById

class Password:
    """
        A password object holds these properties
            - pwdid (GUID)
            - name (Unique name that identifies each password)
            - type (The kind of groupings for the password)
            - description (optional description)
            - sensitiveinfo (JSON dictionary to be encrypted and stored)
            - userid (The logged in userid)
            - createdat
            - lastmodifiedat
    """
    def __init__(
        self,
        pwdname: str,
        pwdtype: str,
        user: User,
        description: str = None
    ):
        # create a new password object
        self.id = uuid.uuid4().hex
        self.pwdname = pwdname
        self.pwdtype = pwdtype
        self.description = description if description is not None else pwdname
        self.auth_user = user
        self.created_at = self.__processDateTime(None)
        self.lastmodified_at = self.__processDateTime(None)
        self.__checkValidProp(self.pwdname, "Name")
        self.__checkValidProp(self.pwdtype, "Type")
        self.__checkValidProp(self.description, "Description")

    def addSensitiveInfo(self, masterkey: bytes, sensitiveinfo: dict = {}):
        self.sensitiveinfo = self.__encrypt(masterkey, sensitiveinfo)


    def serialize(self):
        return {
            "id": self.id,
            "name": self.pwdname,
            "type": self.pwdtype,
            "description": self.description
        }

    @classmethod
    def convertToPassword(cls, dbpass):
        # convert the user saved in db to a proper user object
        user = getUserById(dbpass['userid'])
        pwd = Password(
            dbpass['name'],
            dbpass['type'],
            user,
            dbpass['description']
        )
        pwd.created_at = cls.__processDateTime(dbpass['createdat'])
        pwd.lastmodified_at = cls.__processDateTime(dbpass['lastmodifiedat'])
        pwd.id = dbpass['userid']
        pwd.sensitiveinfo = dbpass['sensitiveinfo']
        return pwd



    def __checkValidProp(self, prop, propname):
        assert prop is not None, str(propname).capitalize() + " must not be empty"
        assert isinstance(prop, str), str(propname).capitalize() + " must be a string"

    def __processDateTime(self, ts):
        if ts is None:
            return datetime.now().timestamp()
        elif isinstance(ts, datetime):
            return ts.timestamp()
        else:
            return float(ts)

    def __base64encode(self, json_object):
        json_string = json.dumps(json_object)
        return base64.b64encode(json_string.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)

    def __base64decode(self, encoded_string: str):
        json_string = base64.b64decode(encoded_string.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        return json.loads(json_string)

    def __encrypt(self, master_key: bytes, json_obj):
        """
            Accepts a master password and encrypts the sensitive information
        """
        f = Fernet(master_key)
        msg = self.__base64encode(json_obj)
        return f.encrypt(msg.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        
    def __decrypt(self, master_key: bytes, msg: str):
        """
            Accepts a master password and decrypts the sensitive information
        """
        f = Fernet(master_key)
        decrypt_string = f.decrypt(msg.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        return self.__base64decode(decrypt_string)
