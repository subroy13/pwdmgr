# PwdMgr: A Python based lightweight password manager

**Caution: This is a work in progress.**

## Features

1. Lightweight, stores stuffs into simple `csv` file.
2. No internet connection required, the entire application resides in your machine offline.
3. Even if an attacker probes into your machine, all he / she will see is encrypted sensitive info, and they cannot decrypt it without your master password.
4. Your master password is stored using `Scrypt`, hence nobody except you knows the password.


## Requirements

1. Python 3.x
2. pandas
3. cryptography
4. uuid
5. base64

To run the application simply use:

`python3 -m pwdmgr.py start`


## Bug Fixes

You are free to look at the source code to find out bugs and potential security vulnerabilities. Please raise them in GitHub issues.




