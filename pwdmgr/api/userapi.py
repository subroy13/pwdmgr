# This python files handles all the CRUD operations logic
# It abstracts over the DB
from ..models import User
from .. import appdb
from ..config import Config

def createNewUser(user: User):
    query = "INSERT INTO {}(userid, username, useremail, salt, password, createdat, lastmodifiedat, status)\
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);".format(Config.DB_USER_TABLE)
    params = [
        user.id,
        user.username,
        user.useremail,
        user.salt,
        user.password,
        user.created_at,
        user.lastmodified_at,
        user.status
    ]
    rows = appdb.executeQuery(query, params, False)
    return user.serialize()


def getUser(username: str):
    query = "SELECT userid, username, useremail, salt, password, createdat, lastmodifiedat, status\
        FROM {} WHERE username = $1 LIMIT 1;".format(Config.DB_USER_TABLE)
    params = [username]
    rows = appdb.executeQuery(query, params, True)
    if len(rows) == 0:
        return None
    else:
        user = User.convertToUser(rows[0])
        return user


def getUserById(userid: str):
    query = "SELECT userid, username, useremail, salt, password, createdat, lastmodifiedat, status\
        FROM {} WHERE userid = $1 LIMIT 1;".format(Config.DB_USER_TABLE)
    params = [userid]
    rows = appdb.executeQuery(query, params, True)
    if len(rows) == 0:
        return None
    else:
        user = User.convertToUser(rows[0])
        return user