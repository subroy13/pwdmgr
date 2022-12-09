# This python files handles all the CRUD operations logic
# It abstracts over the DB
from ..models import Password
from .. import appdb
from ..config import Config

def createNewPassword(pwd: Password):
    query = "INSERT INTO {}(name, type, description, sensitiveinfo, userid, createdat, lastmodifiedat)\
        VALUES ($1, $2, $3, $4, $5, $6, $7);".format(Config.DB_PWD_TABLE)
    params = [
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
