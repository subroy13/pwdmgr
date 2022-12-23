# This python files handles all the CRUD operations logic
# It abstracts over the DB
from ..models import User
from .. import appdb
from ..database import Database
import time, os, pyotp


def createNewUser(user: User, password: str):
    query = "INSERT INTO {}(userid, username, useremail, salt, password, qrseed, createdat, lastmodifiedat, status)\
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);".format(Database.DB_USER_TABLE)
    params = [
        user.id,
        user.username,
        user.useremail,
        user.salt,
        user.password,
        user.qr_seed,
        user.created_at,
        user.lastmodified_at,
        user.status
    ]
    rows = appdb.executeQuery(query, params, False)
    output = user.serialize()
    x = user.decrypt_totp_seed(user.qr_seed, password)
    output['qr_seed'] = pyotp.totp.TOTP(x).provisioning_uri(name = user.username, issuer_name='pwdmgr@subroy13')
    return output

def deleteUser(userid: str):
    query = "DELETE FROM {} WHERE userid = $1;".format(Database.DB_PWD_TABLE)
    rows = appdb.executeQuery(query, [userid], False)
    query = "DELETE FROM {} WHERE userid = $1;".format(Database.DB_USER_TABLE)
    rows = appdb.executeQuery(query, [userid], False)
    return userid

def softDeleteUser(userid: str):
    query = "UPDATE {} SET STATUS = $1, lastmodifiedat = $2 WHERE userid = $3;".format(Database.DB_USER_TABLE)
    params = [
        User.STATUS_INACTIVE,
        int(time.time()),
        userid
    ]
    rows = appdb.executeQuery(query, params, False)
    return userid


def getUser(username: str):
    query = "SELECT userid, username, useremail, salt, password, qrseed, createdat, lastmodifiedat, status\
        FROM {} WHERE username = $1 LIMIT 1;".format(Database.DB_USER_TABLE)
    params = [username]
    rows = appdb.executeQuery(query, params, True)
    if len(rows) == 0:
        return None
    else:
        user = User.convertToUser(rows[0])
        return user


def getUserById(userid: str):
    query = "SELECT userid, username, useremail, salt, password, qrseed, createdat, lastmodifiedat, status\
        FROM {} WHERE userid = $1 LIMIT 1;".format(Database.DB_USER_TABLE)
    params = [userid]
    rows = appdb.executeQuery(query, params, True)
    if len(rows) == 0:
        return None
    else:
        user = User.convertToUser(rows[0])
        return user