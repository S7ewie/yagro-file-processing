from config import config
from psycopg2 import *

class DBConnection:
    def __init__(self):
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        self.conn = connect(**params)
        # create a new cursor
        self.cur = self.conn.cursor()

                
    
    def close_connection(self):
        self.cur.close()
        self.conn.close()