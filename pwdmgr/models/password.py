import os, json, uuid, base64
from datetime import datetime
from cryptography.fernet import Fernet

from ..config import Config 
from .user import User


class Password:
    """
        A password object holds these things
            - PwdId (Password Id - GUID)
            - Name  (Unique name that identifies each password)
            - Type  (Some kind of groupings that you want)
            - Description (Some searchable string, by default same as the name)
            - SensitiveInfo (The encrypted version of base64encoded JSON containing all sensitive information)
            - Userid (The id of the user who is associated with this password)
            - created_at
            - lastmodified_at
    """
    def __init__(
        self,
        pwdname: str,
        user: User,
        pwdtype: str,
        description: str = None,
        sensitive_info: str = None,
        created_at = None,
        lastmodified_at = None,
        pwd_id: str = None
    ): 
        self.pwdname = pwdname
        self.pwdtype = pwdtype
        self.auth_user = user
        self.id = pwd_id if pwd_id is not None else uuid.uuid4().hex 
        self.created_at = self.__processDateTime(created_at)
        self.lastmodified_at = self.__processDateTime(lastmodified_at)        
        self.description = description if description is not None else pwdname
        self.sensitive_info = sensitive_info
        self.__checkValidProp(self.pwdname, "Name")
        self.__checkValidProp(self.pwdtype, "Type")
        self.__checkValidProp(self.description, "Description")

    
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

    def addSensitiveInformation(self, key: str, value, master_pwd: str): 
        """
            - Decrypt the current sensitive information
            - Add a sensitive information
            - Encrypt it back
        """
        master_key = self.auth_user.generateMasterKey(master_pwd)
        if self.sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master password used for decryption")
        else:
            info_json_string = {}
        if key in info_json_string:
            raise KeyError("Key already exists!")
        else:
            info_json_string[key] = value
        self.sensitive_info = self.__encrypt(master_key, info_json_string)

    def bulkAddSensitiveInformation(self, items: dict, master_pwd: str): 
        """
            - Decrypt the current sensitive information
            - Add a sensitive information
            - Encrypt it back
        """
        master_key = self.auth_user.generateMasterKey(master_pwd)
        if self.sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master password used for decryption")
        else:
            info_json_string = {}
        for key in items:
            if key in info_json_string:
                raise KeyError("Key " + key + " already exists!")
            else:
                info_json_string[key] = items[key]
        self.sensitive_info = self.__encrypt(master_key, info_json_string)

    
    def updateSensitiveInformation(self, key, newvalue, master_pwd):
        """
            - Decrypt the current sensitive information
            - Update a sensitive information
            - Encrypt it back
        """
        master_key = self.auth_user.generateMasterKey(master_pwd)
        if self.sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master password used for decryption")
        else:
            info_json_string = {}
        if key not in info_json_string:
            raise KeyError("Key does not exist!")
        else:
            info_json_string[key] = newvalue
        self.sensitive_info = self.__encrypt(master_key, info_json_string)


    def deleteSensitiveInformation(self, key, master_pwd):
        """
            - Decrypt the current sensitive information
            - Delete the sensitive information key
            - Encrypt it back
        """
        master_key = self.auth_user.generateMasterKey(master_pwd)
        if self.sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master password used for decryption")
        else:
            info_json_string = {}
        if key not in info_json_string:
            raise KeyError("Key does not exist!")
        else:
            del info_json_string[key]
        self.sensitive_info = self.__encrypt(master_key, info_json_string)

    def render(self, master_pwd):
        """
            Decrypt the password and show the JSON
        """
        if self.sensitive_info is None:
            return {}
        else:
            try: 
                master_key = self.auth_user.generateMasterKey(master_pwd)
                return self.__decrypt(master_key, self.sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master password used for decryption")

    
    