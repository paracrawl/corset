#!/bin/bash
ROOT=/opt/dp

cd $ROOT/back
source venv/bin/activate

redis-server conf/redis.conf
nohup celery --workdir $ROOT/back -A back.tasks.tasks.celery worker --loglevel=info \
                    --logfile=$ROOT/back/data/logs/celery-worker.log &

cd $ROOT/back/api
if [ -n "$DEBUG" ] && [ "$DEBUG" != "0" ]; then
  FLASK_ENV=development FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 5000
else
  gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile $ROOT/back/data/logs/gunicorn-api.log --error-logfile $ROOT/back/data/logs/gunicorn-api-error.log app:app
fi

tail -f /dev/null
