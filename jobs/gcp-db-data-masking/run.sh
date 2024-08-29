#!/bin/bash
root_dir="/opt/app-root"
cd $root_dir

echo "recreating sandbox db"
gcloud sql instances restart "${DB_NAME}-sandbox"

gcloud --quiet sql databases delete $DB_NAME --instance="${DB_NAME}-sandbox"
gcloud --quiet sql databases create $DB_NAME --instance="${DB_NAME}-sandbox"

echo "loading dump into sandbox db"
gcloud --quiet sql import sql "${DB_NAME}-sandbox" "gs://${DB_NAME}-dump-${ENV}/${DB_NAME}.sql.gz" --database=$DB_NAME --user=$DB_USER

touch readonly.sql

echo "writing grants to users ..."

echo "GRANT USAGE ON SCHEMA public TO readonly;" >> readonly.sql
echo "GRANT SELECT ON ALL TABLES IN SCHEMA public to readonly;" >> readonly.sql
echo "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;" >> readonly.sql

echo "GRANT USAGE ON SCHEMA public TO auth;" >> readonly.sql
echo "GRANT SELECT ON ALL TABLES IN SCHEMA public to auth;" >> readonly.sql
echo "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO auth;" >> readonly.sql
echo "GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO auth;" >> readonly.sql

echo "applying readonly user changes ..."
gsutil cp readonly.sql "gs://${DB_NAME}-dump-${ENV}/"
gcloud --quiet sql import sql "${DB_NAME}-sandbox" "gs://${DB_NAME}-dump-${ENV}/readonly.sql" --database=$DB_NAME --user=$DB_USER
gcloud --quiet sql import sql "${DB_NAME}-sandbox" "gs://${DB_NAME}-dump-${ENV}/mask.sql" --database=$DB_NAME --user=$DB_USER
