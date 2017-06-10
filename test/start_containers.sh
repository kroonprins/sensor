#!/bin/bash

echo "Starting activemq"
docker run --name activemq -p 61616:61616 -p 8161:8161 -d rmohr/activemq:5.14.3-alpine 2>/dev/null || docker start activemq

echo "Starting mysql"
docker run --name s-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=sensor_data -e MYSQL_USER=mysql -e MYSQL_PASSWORD=mysql -d mysql:8 2>/dev/null || docker start s-mysql

echo "done"
