#!/usr/bin/env bash

API_PATH=https://api.hangang.msub.kr/

TEMPERATURE=`curl -s $API_PATH | jq -r ".temp"`

echo $TEMPERATURE

