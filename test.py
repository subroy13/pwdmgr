from pwdmgr.models.password import Password
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os, base64

salt = b"random_string"
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000)
key = base64.urlsafe_b64encode(kdf.derive("password".encode('ascii')))
print(key)

kdf2 = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=390000)
key2 = base64.urlsafe_b64encode(kdf2.derive("ehllo".encode('ascii')))
print(key2)

x = Password('facebook', 'social', None)
x.addSensitiveInformation('username', 'subroy13', key)
x.addSensitiveInformation('password', 'royfbid', key2)

print(x.peek())
print(x.render(key))
print(x.render(key2))

