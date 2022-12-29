# This python files handles all the CRUD operations logic
# It abstracts over the DB
from ..models import Password, User
from .. import appdb
from .userapi import getUserById
import time, os
from ..database import Database


def createNewPassword(pwd: Password):
    query = "INSERT INTO {}(pwdid, name, type, description, sensitiveinfo, userid, createdat, lastmodifiedat)\
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);".format(Database.DB_PWD_TABLE)
    params = [
        pwd.id,
        pwd.pwdname,
        pwd.pwdtype,
        pwd.description,
        pwd.sensitiveinfo,
        pwd.auth_user.id,
        pwd.created_at,
        pwd.lastmodified_at
    ]
    rows = appdb.executeQuery(query, params, False)
    return pwd.serialize()

def listAllPasswords(user: User):
    query = "SELECT pwdid, name, type, description FROM {} WHERE userid = $1 ORDER BY lastmodifiedat DESC;".format(Database.DB_PWD_TABLE)
    params = [user.id]
    rows = appdb.executeQuery(query, params, True)
    return [{"id": row['pwdid'], "name": row['name'], "type": row['type'], "description": row['description']} for row in rows]

def getPasswordById(pwdid: str):
    query = "SELECT pwdid, name, type, description, sensitiveinfo, userid FROM {} WHERE pwdid = $1 LIMIT 1;".format(Database.DB_PWD_TABLE)
    params = [pwdid]
    rows = appdb.executeQuery(query, params, True)
    if len(rows) == 0:
        return None
    else:
        user = getUserById(rows[0]['userid'])
        if user is None:
            return None
        else:
            pwd = Password(rows[0]['name'], rows[0]['type'], user, rows[0]['description'])
            pwd.id = rows[0]['pwdid']
            pwd.sensitiveinfo = rows[0]['sensitiveinfo']
            return pwd


def updatePassword(pwd: Password):
    query = "UPDATE {} SET type = $1, description = $2, lastmodifiedat = $4 WHERE pwdid = $5;".format(Database.DB_PWD_TABLE)
    params = [pwd.pwdtype, pwd.description, int(time.time()), pwd.id]
    rows = appdb.executeQuery(query, params, False)
    return pwd.serialize()

def deletePassword(pwdid: str):
    query = "DELETE FROM {} WHERE pwdid = $1;".format(Database.DB_PWD_TABLE)
    params = [pwdid]
    rows = appdb.executeQuery(query, params, False)
    return rows


def viewPassword(pwdid: str, master_pwd: str, mfa: str):
    try:
        pwd = getPasswordById(pwdid)
        master_key = pwd.auth_user.generateMasterKey(master_pwd, mfa = mfa)
        return pwd.decryptSensitiveInfo(master_key)
    except Exception as e:
        return None