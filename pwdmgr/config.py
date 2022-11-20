class Config:
    """
        Some common configuration details
    """
    BYTES_ENCODING = "utf8"
    USER_STORAGE = "./data/users.csv"
    PASSWORD_STORAGE = "./data/passwords.csv"

    NAV_MENU_PATHS = [
        {
            "choice": "1", 
            "display_text": "Sign up for a new account",
            "action": "signup"
        },
        {
            "choice": "2", 
            "display_text": "Login into your existing account",
            "action": "login",
            "submenu": [
                {
                    "choice": "1",
                    "display_text": "search password",
                    "action": "search"
                },
                {
                    "choice": "2",
                    "display_text": "create new password and store",
                    "action": "createpass"
                },
                {
                    "choice": "3",
                    "display_text": "modify existing stored password",
                    "action": "editpass"
                },
                {
                    "choice": "4",
                    "display_text": "delete existing stored password",
                    "action": "deletepass"
                },
                {
                    "choice": "5",
                    "display_text": "list all your password metadata",
                    "action": "listpass"
                },
                {
                    "choice": "0",
                    "display_text": "Log out",
                    "action": "logout"
                }
            ]
        }
    ]