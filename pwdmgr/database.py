# Database connection handler class
import sqlite3
import os

class Database:

    DB_USER_TABLE = "users"
    DB_PWD_TABLE = "passwords"

    def __init__(self):
        self.dbpath = os.getenv("APP_DBPATH") 

    def getConnection(self):
        try:
            con = sqlite3.connect(self.dbpath)
            con.row_factory = sqlite3.Row
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

    def executeScript(self, query_script):
        con = self.getConnection()
        try:
            with con:
                result = con.executescript(query_script)

            # close the connection after done
            con.close()
        except Exception as e:
            print(e)
            raise e
    

    def bulkinsert(self, tablename: str, rows: list):
        if len(rows) > 0:
            cols = list(rows[0].keys())
            query = "INSERT INTO {}({}) VALUES ".format(tablename, ",".join(cols))
            params = []
            subquerylist = []
            counter = 1
            for row in rows:
                x = []
                for col in cols:
                    x.append("${}".format(str(counter)))
                    params.append(row[col])
                    counter += 1
                subquerylist.append("( " + ",".join(x) + " )")
            query += (",".join(subquerylist) + ";")
            response = self.executeQuery(query, params, False)

        
        



