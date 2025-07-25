from os import environ

API_ID = int(environ.get('API_ID', 0))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')
# Example format for Koyeb PostgreSQL URL:

DATABASE_URI = environ.get("DATABASE_URI")
DATABASE_NAME = environ.get("DATABASE_NAME", "autodelete")
COLLECTION_NAME = environ.get("COLLECTION", "chats")


# Support multiple admin user IDs
ADMINS = list(map(int, environ.get('ADMINS', '0').split()))

DEL_TIME = int(environ.get('DEL_TIME', 600))
