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
def searchPassword(dbuser: User, master_pwd: str, searchstring: str):
    passdf = pd.read_csv(Config.PASSWORD_STORAGE)
    passdf['searchfield'] = passdf['Name'].str.lower() + " " + passdf['Type'].str.lower() + " " + passdf['Description'].str.lower()
    matches = passdf.loc[passdf['searchfield'].str.contains(searchstring)]
    if matches.shape[0] > 0:
        pwd = Password(
            pwd_id=matches.iloc[0]['PwdId'],
            pwdname=matches.iloc[0]['Name'],
            pwdtype=matches.iloc[0]['Type'],
            sensitive_info=matches.iloc[0]['SensitiveInfo'],
            created_at=matches.iloc[0]['CreatedAt'],
            lastmodified_at=matches.iloc[0]['LastModifiedAt'],
            description=matches.iloc[0]['Description'],
            user = dbuser
        )
        return (pwd.pwdname, pwd.pwdtype, pwd.description, pwd.render(master_pwd))
    else:
        return (None, None, None, None)





    
