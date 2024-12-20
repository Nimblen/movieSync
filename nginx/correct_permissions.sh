#!/bin/sh

chown -R www-data:www-data /usr/share/nginx/html/static/
chown -R www-data:www-data /usr/share/nginx/html/media/


chmod -R 755 /usr/share/nginx/html/static/
chmod -R 755 /usr/share/nginx/html/media/   

exec "$@"