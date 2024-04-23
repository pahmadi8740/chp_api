#!/bin/bash
envsubst '$DJANGO_SERVER_ADDR,$STATIC_SERVER_ADDR,$FLOWER_DASHBOARD_ADDR,$NEXTJS_SERVER_ADDR' < /tmp/default.conf > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
