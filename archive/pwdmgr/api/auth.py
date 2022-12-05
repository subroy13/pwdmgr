###################
# This file contains functionalities about user login / signup / validation
# It handles the database operations with the model
##################
import pandas as pd
from datetime import datetime

from ..config import Config
from ..models import User

def __getUserByUsername(username: str):
    # Fetch the user using the username
    userdf = pd.read_csv(Config.USER_STORAGE)
    matched_user = userdf.loc[userdf['Username'] == username]
    if matched_user.shape[0] > 0:
        user = User(
            username = matched_user.iloc[0]['Username'], 
            salt=matched_user.iloc[0]['Salt'],
            password_crypt=matched_user.iloc[0]['PasswordCrypt'],
            created_at=datetime.utcfromtimestamp(matched_user.iloc[0]['CreatedAt']),
            lastmodified_at=datetime.utcfromtimestamp(matched_user.iloc[0]['LastModifiedAt']),
            user_id = matched_user.iloc[0]['Userid']
        )
        return user        
    else:
        return None

def __saveUser(user: User):
    # Saves a new user
    userdf = pd.read_csv(Config.USER_STORAGE)
    ts = datetime.now().timestamp()
    newuser_row = pd.Series({
        "Userid": user.id,
        "Username": user.username,
        "Salt": user.salt,
        "PasswordCrypt": user.password_crypt,
        "CreatedAt": ts,
        "LastModifiedAt": ts
    })
    pd.concat([userdf, newuser_row.to_frame().T], ignore_index=True).to_csv(Config.USER_STORAGE, index=False)

def __updateUser(user: User):
    # Updates an existing user
    userdf = pd.read_csv(Config.USER_STORAGE)
    userdf.loc[userdf['Userid'] == user.id, ['Username', 'Salt', 'PasswordCrypt', 'LastModifiedAt']] = [user.username, user.salt, user.password_crypt, datetime.now().timestamp()]
    userdf.to_csv(Config.USER_STORAGE, index = False)


# Function to perform signup logic
def signUpUser(
    username: str, 
    password: str,
    confirm_password: str
):
    assert password == confirm_password, "The password does not match with the confirmed password"
    dbuser = __getUserByUsername(username)
    assert dbuser is None, "The username is already taken. Please use another user name"
    newuser = User(username=username, password=password)
    __saveUser(newuser)


# Function to perform login logic
def signInUser(
    username: str,
    password: str
): 
    dbuser = __getUserByUsername(username)
    assert dbuser is not None, "Username does not exist!"
    verified = dbuser.verify_password_crypt(password)
    assert verified, "Password mismatch! Please type the correct password."
    return dbuser       # return the logged in user
