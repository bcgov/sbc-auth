CREATE USER notifyuser WITH PASSWORD 'notify' SUPERUSER;
ALTER USER notify WITH LOGIN;

CREATE DATABASE notify
    WITH
    OWNER = notify
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
