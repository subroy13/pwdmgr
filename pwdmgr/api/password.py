#########################
# Functions for managing and storing passwords
#########################
import pandas as pd
from datetime import datetime

from ..models import User, Password
from ..config import Config

def __savePassword(password: Password):
    # Saves a new password
    passdf = pd.read_csv(Config.PASSWORD_STORAGE)
    ts = datetime.now().timestamp()
    newpass_row = pd.Series({
        "PwdId": password.id,
        "Name": password.pwdname,
        "Type": password.pwdtype,
        "Description": password.description,
        "SensitiveInfo": password.sensitive_info,
        "Userid": password.auth_user.id,
        "CreatedAt": ts,
        "LastModifiedAt": ts
    })
    pd.concat([passdf, newpass_row.to_frame().T], ignore_index=True).to_csv(Config.PASSWORD_STORAGE, index=False)

def __updatePassword(password: Password):
    # Updates an existing password
    passdf = pd.read_csv(Config.PASSWORD_STORAGE)
    passdf.loc[passdf['PwdId'] == password.id, ['Name', 'Type', 'Description', 'SensitiveInfo', 'LastModifiedAt']] = [
        password.pwdname,
        password.pwdtype,
        password.description,
        password.sensitive_info,
        datetime.now().timestamp()
    ]
    passdf.to_csv(Config.PASSWORD_STORAGE, index = False)


# Requires logged in user
# lists all passwords for the logged in user
def listPasswords(dbuser: User, password: str):
    # verify if valid user
    verified = dbuser.verify_password_crypt(password)
    assert verified, "Password Mismatch! Please type correct password"
    passdf = pd.read_csv(Config.PASSWORD_STORAGE)
    subdf = passdf.loc[passdf['Userid'] == dbuser.id]
    passlist = []
    for index, row in subdf.iterrows():
        passlist.append(Password(
            pwdname=row['Name'],
            pwdtype=row['Type'],
            description=row['Description'],
            user=dbuser,
            sensitive_info=row['SensitiveInfo'],
            pwd_id=row['PwdId'],
            created_at=row['CreatedAt'],
            lastmodified_at=row['LastModifiedAt']
        ))
    return passlist

# Requires logged in user
# create a password for the user
def createPassword(
    dbuser: User, 
    master_pwd: str,
    pwdname: str,
    pwdtype: str,
    pwddescription: str = None,
    pwd_obj: dict = {},
):
    pwddescription = pwddescription if pwddescription is not None and pwddescription != "" else None
    newpass = Password(
        pwdname=pwdname,
        pwdtype=pwdtype,
        description=pwddescription,
        user=dbuser
    )
    newpass.bulkAddSensitiveInformation(pwd_obj, master_pwd)
    __savePassword(newpass)


# Required a logged in user
# show a password for the user
def searchPassword(dbuser: User, searchstring: str):
    MAX_LIMIT = 5
    passdf = pd.read_csv(Config.PASSWORD_STORAGE)
    passdf['searchfield'] = passdf['Name'].str.lower() + " " + passdf['Type'].str.lower() + " " + passdf['Description'].str.lower()
    matches = passdf.loc[passdf['searchfield'].str.contains(searchstring) & passdf['Userid'] == dbuser.id].reset_index(drop = True).iloc[:MAX_LIMIT]
    pwdlist = []
    for i, row in matches.iterrows():
        pwd = Password(
            pwd_id=matches.iloc[i]['PwdId'],
            pwdname=matches.iloc[i]['Name'],
            pwdtype=matches.iloc[i]['Type'],
            sensitive_info=matches.iloc[i]['SensitiveInfo'],
            created_at=matches.iloc[i]['CreatedAt'],
            lastmodified_at=matches.iloc[i]['LastModifiedAt'],
            description=matches.iloc[i]['Description'],
            user = dbuser
        )
    pwdlist.append(pwd)
    return pwdlist


# Requires a logged in user
# edit a password field
def editPassword(
    dbuser: User, 
    master_pwd: str, 
    pwd: Password,
    editkey: str, 
    editvalue: str
):
    if editkey == "description":
        pwd.description = editvalue
    else:
        actual_key = editkey[16:]
        if editvalue == "":
            # means need to delete the key
            pwd.deleteSensitiveInformation(actual_key, master_pwd)
        else:
            # meeans need to update the key
            pwd.updateSensitiveInformation(actual_key, editvalue, master_pwd)

    # finally update the password
    __updatePassword(pwd)
    

def deletePassword(dbuser: User, master_pwd: str, pwd: Password):
    # Deletes an existing password
    passdf = pd.read_csv(Config.PASSWORD_STORAGE)
    passdf = passdf.loc[passdf['PwdId'] != pwd.id]
    passdf.to_csv(Config.PASSWORD_STORAGE, index = False)



    
