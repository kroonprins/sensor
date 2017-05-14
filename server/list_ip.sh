#!/bin/bash

for container in `grep container_name docker-compose.yml | awk '{ print $2 }'`; do
  ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container")
  printf "%-30s: %s\n" $container $ip
done
