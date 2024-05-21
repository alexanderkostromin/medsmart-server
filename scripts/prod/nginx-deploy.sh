#!/bin/sh -x

rsync -avz ./nginx/ root@med-web:/etc/nginx && ssh root@med-web "nginx -s reload"
ssh med-web "printf \"http://%s\n\" \"\$(curl -s eth0.me)\""; echo https://medsmart.site
