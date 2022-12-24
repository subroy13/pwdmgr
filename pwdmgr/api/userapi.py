# This python files handles all the CRUD operations logic
# It abstracts over the DB
from ..models import User, Password
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

def changeMasterPassword(user: User, oldpass: str, newpass: str, mfa: str):
    """
        1. Create a temporary table.
        2. Decrypt passwords from "passwords" table and encrypt and store them in temporary table.
        3. Atomic Block:
            - Bulk update the encrypted sensitive info from temp table. 
            - Update the password_crypt fields in the "users" table.
    """
    query = "CREATE TABLE tmppass(id INTEGER NOT NULL, sensitiveinfo VARCHAR NULL);"
    appdb.executeQuery(query, [], False)
    
    # fetch all passwords
    query = "SELECT pwdid, name, type, description FROM {} WHERE userid = $1 ORDER BY lastmodifiedat DESC;".format(Database.DB_PWD_TABLE)
    params = [user.id]
    rows = appdb.executeQuery(query, params, True)
    passlist = [Password.convertToPassword(row) for row in rows]

    # generate master keys
    oldmasterkey = user.generateMasterKey(oldpass, mfa = mfa)
    user.updatePassword(oldpass, newpass)
    newmasterkey = user.generateMasterKey(newpass, mfa=mfa)

    # update the senstive info into temporary table
    rowsToInsert = []
    for pwd in passlist:
        pwd.addSensitiveInfo(newmasterkey, pwd.decryptSensitiveInfo(oldmasterkey))
        rowsToInsert.append({"id": pwd.id, "sensitiveinfo": pwd.sensitiveinfo})
    appdb.bulkinsert("tmppass", rowsToInsert)


    # create a transaction block
    transaction_query = "\
        BEGIN TRANSACTION;\
            UPDATE {} SET sensitiveinfo = t1.sensitiveinfo FROM\
            (SELECT id, sensitiveinfo FROM tmppass) AS t1\
            WHERE {}.id = t1.id;\
            UPDATE {} SET password = $1, qrseed = $2 WHERE userid = $3;\
        END TRANSACTION;".format(
            Database.DB_PWD_TABLE, 
            Database.DB_PWD_TABLE,
            Database.DB_USER_TABLE
        )
    params = [user.password, user.qr_seed, user.id]
    appdb.executeQuery(transaction_query, params, False)
    
