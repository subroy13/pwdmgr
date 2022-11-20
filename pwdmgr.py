import os
from getpass import getpass
import datetime as dt

from pwdmgr import (
    signInUser, 
    signUpUser,
    searchPassword,
    createPassword,
    editPassword,
    deletePassword,
    listPasswords
)
from pwdmgr.config import Config
from pwdmgr.models import Password

class PasswordManager:
    """
        This is the main application class for the Password Manager
        This run an infinite event loop, which prompts the user to take any action.
    """
    def __init__(self):
        self.auth_user = None
        self.cur_menu = Config.NAV_MENU_PATHS

    def showWelcomeMessage(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 50)
        print("=" * 10 + " PASSWORD MANAGER " + "=" * 10)
        print("-" * 50)
        print('Please follow the on screen guidelines to help you navigate through the application.')
        print("Welcome {}, you can type `exit` or `quit` when you are done".format("Guest User" if self.auth_user is None else self.auth_user.username))
        print("=" * 50)

    def waitForKeypress(self):
        x = input("Press any key to continue: ")

    def showNavChoices(self, choice_list):
        for choice in choice_list:
            print("\t{}: {}".format(choice['choice'], choice["display_text"]))
        user_choice = input("Please select one of the above options: ").lower()
        if user_choice.lower() in ['quit', 'exit']:
            return {"action": "quit"}
        user_choice_item = None
        for choice in choice_list:
            if user_choice == choice['choice']:
                user_choice_item = choice
        return user_choice_item

    def doSignUp(self):
        username = input('Input your preferred user name: ')
        password = getpass('Input your preferred master password: ')
        confirm_password = getpass('Confirm your master password: ')
        signUpUser(username, password, confirm_password)
        print('Congrats! you have successfully created an account.')
        self.waitForKeypress()

    def doLogin(self):
        username = input('Input your registered user name: ')
        password = getpass('Input your master password: ')
        auth_user = signInUser(username, password)
        self.auth_user = auth_user
        print('You have successfully logged in.')
        self.waitForKeypress()

    def doSearch(self):
        searchtext = input('Input your search text: ')
        plain_passes: list[Password] = searchPassword(self.auth_user, searchtext)
        print("We found {} many passwords matching your search input.".format(len(plain_passes)))

        if len(plain_passes) > 0:
            while True:
                try:
                    for i in range(len(plain_passes)):
                        print("{}: {} - {} - {}".format(
                            i + 1,
                            plain_passes[i].pwdname,
                            plain_passes[i].pwdtype,
                            plain_passes[i].description[:100] + "..."
                        ))
                    x = int(input('Select the password number you wish to display: '))
                    password = getpass('Input your master password: ')
                    print(plain_passes[int(x - 1)].pwdname, " : ", plain_passes[int(x - 1)].render(password))
                    self.waitForKeypress()
                    break
                except Exception as e:
                    print("\n")
                    raise e
        else:
            self.waitForKeypress()

    def doListPassword(self):
        PAGE_SIZE = 10
        master_pwd = getpass("Input your master password: ")
        plain_passes: list[Password] = listPasswords(self.auth_user, master_pwd)
        print("We found {} passwords for your account. ".format(len(plain_passes)))
        
        more_to_show = True 
        i = 0
        while i < len(plain_passes) and more_to_show:
            print("Sl. No.\t|Name\t|Type\t|Description")
            for j in range(i, min(i+PAGE_SIZE, len(plain_passes))):
                print("{}:\t{}\t{}\t{}".format(
                        j + 1,
                        plain_passes[j].pwdname,
                        plain_passes[j].pwdtype,
                        plain_passes[j].description[:100] + "..."
                ))
            i += PAGE_SIZE
            if i < len(plain_passes):
                user_wants_more = input("Please 'y' to display more: ").lower()
                if user_wants_more != "y":
                    more_to_show = False

        print("\n")
        self.waitForKeypress()

        
    def doCreatePasswordAndStore(self):
        pwdname = input('Input your password name: ')
        pwdtype = input('Input what kind of password this is: ')
        description = input("Some additional description (Optional) [leave blank if you don't have any description to add]: ")
        print('In the next few lines, describe what kind of sensitive information you want to store. You can write key:value pairs in each line. Keep the last line blank when you are done.')
        pwd_obj = {}
        while True:
            try:
                pwd_key, pwd_val = input().split(":")
                pwd_obj[pwd_key] = pwd_val
            except Exception as e:
                # this means blank line
                break
        password = getpass('Input your master password: ')
        createPassword(self.auth_user, password, pwdname, pwdtype, description, pwd_obj)
        print("Your password {} is stored securely encrypted with your master password.".format(pwdname))
        self.waitForKeypress()
    
    def doEditPassword(self):
        searchtext = input('Search the password you want to edit: ')
        plain_passes: list[Password] = searchPassword(self.auth_user, searchtext)
        print("We found {} many passwords matching your search input.".format(len(plain_passes)))

        while True:
            try:
                for i in range(len(plain_passes)):
                    print("{}: {} - {} - {}".format(
                        i + 1,
                        plain_passes[i].pwdname,
                        plain_passes[i].pwdtype,
                        plain_passes[i].description[:100] + "..."
                    ))
                x = int(input('Select the password number you wish to edit: '))
                password = getpass('Input your master password: ')
                pwd_to_edit = plain_passes[int(x - 1)]
                editfields = pwd_to_edit.getEditableFields(password)
                while True:
                    try: 
                        for j in range(len(editfields)):
                            print("{}: {}".format(j+1, editfields[j]))
                        y = int(input('Select the field you want to edit in the password (Select 2 to add new field to sensitive info): '))
                        if (y == 2):
                            editfieldkey = input('Input the new field you want to add: ')
                            val = input('Input the new value for the field: ')
                            editPassword(self.auth_user, password, pwd_to_edit, "sensitive_info->NEW->" + editfieldkey, val)
                        else:
                            val = input('Input the new value for the corresponding field (Keep it blank if you want to delete the key): ')
                            editPassword(self.auth_user, password, pwd_to_edit, editfields[int(y - 1)], val)
                        print("Your password has changed successfully")
                        self.waitForKeypress()
                        break
                    except Exception as e:
                        print("\n")
                break
            except Exception as e:
                print("\n")
                raise e

    def doDeletePassword(self):
        searchtext = input('Search the password you want to edit: ')
        plain_passes: list[Password] = searchPassword(self.auth_user, searchtext)
        print("We found {} many passwords matching your search input.".format(len(plain_passes)))
        while True:
            try:
                for i in range(len(plain_passes)):
                    print("{}: {} - {} - {}".format(
                        i + 1,
                        plain_passes[i].pwdname,
                        plain_passes[i].pwdtype,
                        plain_passes[i].description[:50] + "..."
                    ))
                x = int(input('Select the password number you wish to delete: '))
                password = getpass('Input your master password: ')
                pwd_to_delete = plain_passes[int(x - 1)]
                confirm = input("Are you sure you wish to delete password {}? ".format(pwd_to_delete.pwdname))
                if confirm.lower() in ["y", "yes", "yeah", "ok"]:
                    deletePassword(self.auth_user, password, pwd_to_delete)
                    print("Password deleted successfully.")
                    self.waitForKeypress()
                
            except Exception as e:
                print("\n")
                raise e


    def start(self):

        # This is the event loop
        while True:
            try:
                self.showWelcomeMessage()
                user_choice = self.showNavChoices(self.cur_menu)
                if user_choice is not None:
                    if user_choice['action'] == 'quit':
                        print("Good Bye! [{}]".format(dt.datetime.now()))
                        break   # exit the application
                    elif user_choice['action'] == 'signup':
                        self.doSignUp()
                    elif user_choice['action'] == 'login':
                        self.doLogin()
                        self.cur_menu = user_choice['submenu']
                    elif user_choice['action'] == "search":
                        self.doSearch()
                    elif user_choice['action'] == "createpass":
                        self.doCreatePasswordAndStore()
                    elif user_choice['action'] == "editpass":
                        self.doEditPassword()
                    elif user_choice['action'] == "deletepass":
                        self.doDeletePassword()
                    elif user_choice['action'] == "listpass":
                        self.doListPassword()
                    elif user_choice['action'] == "logout":
                        self.auth_user = None
                        self.cur_menu = Config.NAV_MENU_PATHS

            except Exception as e:
                print("Error: ", e)
                self.waitForKeypress()


if __name__ == "__main__":
    app = PasswordManager()
    app.start()
