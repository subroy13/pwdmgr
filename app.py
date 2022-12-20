import os
from dotenv import load_dotenv
load_dotenv()

from pwdmgr import app 

if __name__ == "__main__":
    app.run(debug = True)