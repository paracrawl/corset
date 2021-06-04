#!/bin/bash
ROOT=/opt/dp/front

cd $ROOT
source venv/bin/activate

if [ -n "$DEBUG" ] && [ "$DEBUG" != "0" ]; then
  FLASK_ENV=development FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 5000
else
  gunicorn -w 4 -k gevent -b 0.0.0.0:5000 --access-logfile $ROOT/data/logs/gunicorn.log --error-logfile $ROOT/data/logs/gunicorn-error.log app:app
fi

tail -f /dev/null
