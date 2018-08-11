import sqlite3
from config import DIR_PATH, DATABASE_FILE

databaseName = DIR_PATH+DATABASE_FILE

class dbExecutor:
    def __init__(self):
        return

    @staticmethod
    def insertOne(ad):
        conn = sqlite3.connect(databaseName)
        cursor = conn.cursor()
        query = 'INSERT INTO TP_LINK(DEV_NAME,MAC_ADDR,IP_ADDR,LEASE_TIME,DATE) VALUES (?,?,?,?,?)'
        cursor.execute(query, ad)
        conn.commit()
        conn.close()