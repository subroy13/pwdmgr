import json 
import base64
from cryptography.fernet import Fernet
from ..config import Config


class Password:
    """
        A password object holds 4 things
            - Name  (Unique name that identifies each password)
            - Type  (Some kind of groupings that you want)
            - Description (Some searchable string, by default same as the name)
            - SensitiveInfo (The encrypted version of base64encoded JSON containing all sensitive information)
    """
    def __init__(self, pwdname: str, pwdtype: str = None, description: str = None, sensitive_info: str = None):
        self.__pwdname = pwdname
        self.__pwdtype = pwdtype if pwdtype is not None else 'Others'
        self.__description = description if description is not None else pwdname
        self.__sensitive_info = sensitive_info
        self.__checkValidProp(self.__pwdname, "Name")
        self.__checkValidProp(self.__pwdtype, "Type")
        self.__checkValidProp(self.__description, "Description")

    def __checkValidProp(self, prop, propname):
        assert prop is not None, str(propname).capitalize() + " must not be empty"
        assert isinstance(prop, str), str(propname).capitalize() + " must be a string"

    def __base64encode(self, json_object):
        json_string = json.dumps(json_object)
        return base64.b64encode(json_string.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)

    def __base64decode(self, encoded_string: str):
        json_string = base64.b64decode(encoded_string.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        return json.loads(json_string)

    def __encrypt(self, master_key, json_obj):
        """
            Accepts a master password and encrypts the sensitive information
        """
        f = Fernet(master_key)
        msg = self.__base64encode(json_obj)
        return f.encrypt(msg.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        
    def __decrypt(self, master_key, msg: str):
        """
            Accepts a master password and decrypts the sensitive information
        """
        f = Fernet(master_key)
        decrypt_string = f.decrypt(msg.encode(Config.BYTES_ENCODING)).decode(Config.BYTES_ENCODING)
        return self.__base64decode(decrypt_string)


    def addSensitiveInformation(self, key, value, master_key): 
        """
            - Decrypt the current sensitive information
            - Add a sensitive information
            - Encrypt it back
        """
        if self.__sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.__sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master key used for decryption")
        else:
            info_json_string = {}
        if key in info_json_string:
            raise KeyError("Key already exists!")
        else:
            info_json_string[key] = value
        self.__sensitive_info = self.__encrypt(master_key, info_json_string)

    
    def updateSensitiveInformation(self, key, newvalue, master_key):
        """
            - Decrypt the current sensitive information
            - Update a sensitive information
            - Encrypt it back
        """
        if self.__sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.__sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master key used for decryption")
        else:
            info_json_string = {}
        if key not in info_json_string:
            raise KeyError("Key does not exist!")
        else:
            info_json_string[key] = newvalue
        self.__sensitive_info = self.__encrypt(master_key, info_json_string)


    def deleteSensitiveInformation(self, key, master_key):
        """
            - Decrypt the current sensitive information
            - Delete the sensitive information key
            - Encrypt it back
        """
        if self.__sensitive_info is not None:
            try:
                info_json_string = self.__decrypt(master_key, self.__sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master key used for decryption")
        else:
            info_json_string = {}
        if key not in info_json_string:
            raise KeyError("Key does not exist!")
        else:
            del info_json_string[key]
        self.__sensitive_info = self.__encrypt(master_key, info_json_string)

    def render(self, master_key):
        """
            Decrypt the password and show the JSON
        """
        if self.__sensitive_info is None:
            return {}
        else:
            try: 
                return self.__decrypt(master_key, self.__sensitive_info)
            except Exception as e:
                raise PermissionError("Invalid master key used for decryption")

    def getData(self):
        """
            Gets the data which we need to store
        """
        return {
            "Name": self.__pwdname,
            "Type": self.__pwdtype,
            "Description": self.__description,
            "SensitiveInfo": self.__sensitive_info
        }






