# PwdMgr: A Python based lightweight password manager

The aim is to create a password manager which is lightweight, user-friendly and open source so that even under zero-trust assumption, the users would be comfortable in storing the passwords in this application.

## Features

1. Lightweight, stores stuffs into simple `sqlite` database file.
2. No internet connection required, the entire application resides in your machine offline.
3. Even if an attacker probes into your machine, all he / she will see is encrypted sensitive info, and they cannot decrypt it without your master password.
4. Your master password is stored using `Scrypt`, hence nobody except you knows the password.
5. The encryption key is a combination of your master password and an app secret stored in the .env file of the repository. (*You will need this .env file for hosting your own version of the app, but for security reasons it is omitted here. Please see details below.*)
6. To use the app encryption secret for encryption and decryption purposes, user must authenticate themselves using their master password and an time based OTP provided by any MFA authenticator app (Google Authenticator, Microsoft Authenticator, etc.)


## Requirements

1. Python 3.x
2. flask
3. flask-wtf
4. cryptography
5. uuid
6. base64
7. python-dotenv
8. pyotp

To run the application simply use:

`python3 app.py`

The `.env` file should contain at least the following lines:

```
APP_DBPATH = "./app.sqlite"
APP_BYTES_ENCODING = "utf-8"
APP_SECRET = "your-app-secret-used-for-csrf-token-protection-on-form-resubmission"
APP_ENCRYPT_SECRET = "your-app-secret-key-used-for-encrypting-sensitive-password-information"
```


## Bug Fixes

You are free to look at the source code to find out bugs and potential security vulnerabilities. Please raise them in GitHub issues.
