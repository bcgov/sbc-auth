import os
from dotenv import load_dotenv, find_dotenv

# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())


class Config(object):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    WEEKLY_REPORT_RECIPIENTS = os.getenv('WEEKLY_REPORT_RECIPIENTS', '')
    WEEKLY_REPORT_DATES = os.getenv('WEEKLY_REPORT_DATES', '')
    ERROR_EMAIL_RECIPIENTS = os.getenv('ERROR_EMAIL_RECIPIENTS', '')
    ENVIRONMENT = os.getenv('ENVIRONMENT', '')    

    # POSTGRESQL
    PG_USER = os.getenv('PG_USER', '')
    PG_PASSWORD = os.getenv('PG_PASSWORD', '')
    PG_NAME = os.getenv('PG_DB_NAME', '')
    PG_HOST = os.getenv('PG_HOST', '')
    PG_PORT = os.getenv('PG_PORT', '5432')
    
    if DB_UNIX_SOCKET := os.getenv('DATABASE_UNIX_SOCKET', None):
        SQLALCHEMY_DATABASE_URI = f'postgresql+pg8000://{PG_USER}:{PG_PASSWORD}@/{PG_NAME}?unix_sock={DB_UNIX_SOCKET}/.s.PGSQL.5432'                                      
    else:
        SQLALCHEMY_DATABASE_URI = f'postgresql+pg8000://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}'
    
    NOTIFY_API_URL = f"{os.getenv("NOTIFY_API_URL", "") + os.getenv("NOTIFY_API_VERSION", "")}/notify"
    NOTIFY_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
    NOTIFY_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
    KEYCLOAK_AUTH_TOKEN_URL = os.getenv("KEYCLOAK_AUTH_TOKEN_URL")      


