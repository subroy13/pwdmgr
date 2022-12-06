# Database connection handler class
import sqlite3
from .config import Config

class Database:

    def __init__(self):
        self.dbpath = Config.DB_PATH        

    def getConnection(self):
        try:
            con = sqlite3.connect(self.dbpath)
            return con
        except Exception as e:
            print(e)
            raise RuntimeError("Could not connect to database")

    def executeQuery(self, query, parameters, return_value = False): 
        con = self.getConnection()
        output = None
        try:
            with con:
                result = con.execute(query, parameters)
                if return_value:
                    output = result.fetchall()

            # Try to close the connection after query is done
            con.close()
            return output
        except Exception as e:
            print(e)
            raise e


        



