#!/usr/bin/env bash

# Disable the Datadog Agent based on dyno type
if [ "$DYNOTYPE" == "run" ] || [ "$DYNOTYPE" == "release" ]; then
  DISABLE_DATADOG_AGENT="true"
fi

if [ "$DYNOTYPE" == "web" ] ; then
  DD_SERVICE="tmh_registry-web"
fi



# Set app version based on HEROKU_SLUG_COMMIT
if [ -n "$HEROKU_SLUG_COMMIT" ]; then
  DD_VERSION=$HEROKU_SLUG_COMMIT
fi

# Update the Postgres configuration from above using the Heroku application environment variable
if [ -n "$DATABASE_URL" ]; then
  POSTGREGEX='^postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.*)$'
  if [[ $DATABASE_URL =~ $POSTGREGEX ]]; then
    sed -i "s/<YOUR HOSTNAME>/${BASH_REMATCH[3]}/" "$DD_CONF_DIR/conf.d/postgres.d/conf.yaml"
    sed -i "s/<YOUR USERNAME>/${BASH_REMATCH[1]}/" "$DD_CONF_DIR/conf.d/postgres.d/conf.yaml"
    sed -i "s/<YOUR PASSWORD>/${BASH_REMATCH[2]}/" "$DD_CONF_DIR/conf.d/postgres.d/conf.yaml"
    sed -i "s/<YOUR PORT>/${BASH_REMATCH[4]}/" "$DD_CONF_DIR/conf.d/postgres.d/conf.yaml"
    sed -i "s/<YOUR DBNAME>/${BASH_REMATCH[5]}/" "$DD_CONF_DIR/conf.d/postgres.d/conf.yaml"
  fi
fi
# Update the Redis configuration from above using the Heroku application environment variable
if [ -n "$REDIS_URL" ]; then
  REDISREGEX='^redis://:([^@]+)@([^:]+):([^/]+)$'
  if [[ $REDIS_URL =~ $REDISREGEX ]]; then
    sed -i "s/<YOUR HOSTNAME>/${BASH_REMATCH[2]}/" "$DD_CONF_DIR/conf.d/redisdb.d/conf.yaml"
    sed -i "s/<YOUR PORT>/${BASH_REMATCH[3]}/" "$DD_CONF_DIR/conf.d/redisdb.d/conf.yaml"
    sed -i "s/<YOUR PASSWORD>/${BASH_REMATCH[1]}/" "$DD_CONF_DIR/conf.d/redisdb.d/conf.yaml"
  fi
fi
