#!/bin/sh

envsubst '$${NGINX_HOST},$${NGINX_PORT}' < /config/app.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'
