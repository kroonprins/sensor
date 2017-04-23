#!/bin/bash

echo "Stopping activemq"
docker stop activemq

echo "Stopping mysql"
docker stop s-mysql

echo "done"
