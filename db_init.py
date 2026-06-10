from db import init_database
import os

print("Database Path:", os.path.abspath("assets.db"))

init_database()

print("Database tables created successfully!")