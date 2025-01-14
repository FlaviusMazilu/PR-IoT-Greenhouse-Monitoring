docker build -t nginx-secure .
docker run -p 8050:80 -p 8060:443 --name nginx-secure nginx-secure