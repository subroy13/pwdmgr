from pwdmgr.api import signUpUser, signInUser, createPassword, searchPassword

username = "subroy13"
pwd = "test1234"

# x = signUpUser(username, pwd, pwd)
# print(x)

user = signInUser(username, pwd)
print(user)

# p1 = createPassword(user, pwd, 'Facebook', 'Social', None, {"password": "royfbid", "security question": "your birth place"})

p2 = searchPassword(user, pwd, "facebook")
print(p2)
