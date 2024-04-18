#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python3 hellodjango/manage.py flush --no-input
python3 hellodjango/manage.py migrate
python3 hellodjango/manage.py collectstatic --no-input
exec "$@"