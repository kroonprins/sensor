#!/bin/bash

kubectl get po | tail -n +2 | while read pod ready status restarts age; do
  node=$(kubectl describe po $pod | grep "^Node:" | awk '{print $2}')
  printf "%-50s %-20s %s\n" $pod $status $node
done
