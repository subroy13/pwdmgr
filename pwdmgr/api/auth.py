###################
# This file contains functionalities about user login / signup / validation
##################
import pandas as pd
import uuid
from ..config import Config
from ..models import User


def __getUserByUsername(username: str):
    userdf = pd.read_csv(Config.USER_STORAGE)
    matched_user = userdf.loc[userdf['Username'] == username]
    if matched_user.shape[0] > 0:
        user = User(
            username = matched_user.iloc[0]['Username'], 
            salt=matched_user.iloc[0]['Salt'],
            password_crypt=matched_user.iloc[0]['PasswordHash']
        )
        return user        
    else:
        return None


def signupUser(username: str, password: str):
    # first check if username is duplicating, 
    dbuser = __getUserByUsername(username)
    assert dbuser is None, "Username already exists, please try with a different username"
    user = User(username = username, password=password)
    userdf = pd.read_csv(Config.USER_STORAGE)
    newuser_row = pd.Series(dict({"Userid": uuid.uuid4().hex }, **user.getData()))
    pd.concat([userdf, newuser_row.to_frame().T], ignore_index=True).to_csv(Config.USER_STORAGE, index=False)


def loginUser(username, password):
    # first find the user
    dbuser = __getUserByUsername(username)
    assert dbuser is not None, "Username is not valid"
    login_success, master_key = dbuser.verify_password_crypt(password)
    assert login_success, "Invalid password"
    return master_key
    