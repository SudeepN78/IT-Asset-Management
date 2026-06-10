import os

def get_db():
    print("DB PATH USED:", os.path.abspath("assets.db"))
    return sqlite3.connect("assets.db")
