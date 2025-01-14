FROM nginx:alpine

COPY ./my-app/ /usr/share/nginx/html

COPY ./nginx-selfsigned.crt /etc/nginx/ssl/nginx-selfsigned.crt
COPY ./nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned.key

COPY ./default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]