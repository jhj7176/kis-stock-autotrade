#!/bin/bash

PROJECT=stock-trade
# GROUP=

TODAY=$(date +'%Y%m%d')
echo  "Build Docker for $PROJECT - $1 - $TODAY" 

docker build --tag $PROJECT:${1}latest --tag $PROJECT:${1}$TODAY -f ./Dockerfile .. || exit
docker image tag $PROJECT:${1}latest hyeongjin0319/$PROJECT:${1}latest
docker image tag $PROJECT:${1}latest hyeongjin0319/$PROJECT:${1}$TODAY
docker image push -a hyeongjin0319/$PROJECT

