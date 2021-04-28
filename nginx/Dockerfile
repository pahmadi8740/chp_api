FROM nginx:latest
COPY nginx.conf /etc/nginx/conf.d
RUN apt-get update
RUN apt-get -y install python-certbot-nginx
RUN rm /etc/nginx/conf.d/default.conf
CMD [ "/bin/sh certbot --nginx" ] 
#ENTRYPOINT ["nginx", "-g", "daemon off;"]