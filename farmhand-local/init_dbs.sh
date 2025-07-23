#!/bin/bash
set -e

echo "Creating databases if they do not exist..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname=postgres <<-EOSQL
SELECT 'CREATE DATABASE "farmhand"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'farmhand')\gexec

SELECT 'CREATE DATABASE "farmhand-data"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'farmhand-data')\gexec
EOSQL