#!/usr/bin/env bash

COUNT=`curl -H "Host: api.gather.town" -H "accept: application/json" -H "origin: https://app.gather.town" --compressed -s "https://api.gather.town/api/getRoomInfo?room=0v6GlxIbLfBeki85%5CDEPROMEET+12th" | jq -r ".roomCount"` 

echo $COUNT
