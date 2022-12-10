# This python files handles all the CRUD operations logic
# It abstracts over the DB
from ..models import Password, User
from .. import appdb
from ..config import Config

def createNewPassword(pwd: Password):
    query = "INSERT INTO {}(pwdid, name, type, description, sensitiveinfo, userid, createdat, lastmodifiedat)\
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);".format(Config.DB_PWD_TABLE)
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
    query = "SELECT pwdid, name, type, description FROM {} WHERE userid = $1 ORDER BY lastmodifiedat DESC;".format(Config.DB_PWD_TABLE)
    params = [user.id]
    rows = appdb.executeQuery(query, params, True)
    return [{"id": row['pwdid'], "name": row['name'], "type": row['type'], "description": row['description']} for row in rows]

def updatePassword(pwd: Password):
    query = "UPDATE {} SET type = $1, description = $2, sensitiveinfo = $3, lastmodifiedat = $4 WHERE pwdid = $5;".format(Config.DB_PWD_TABLE)
    params = [pwd.pwdtype, pwd.description, pwd.sensitiveinfo, pwd.lastmodified_at, pwd.id]
    rows = appdb.executeQuery(query, params, False)
    return pwd.serialize()

def deletePassword(pwdid: str):
    query = "DELETE FROM {} WHERE pwdid = $1;".format(Config.DB_PWD_TABLE)
    params = [pwdid]
    rows = appdb.executeQuery(query, params, True)
    return rows

