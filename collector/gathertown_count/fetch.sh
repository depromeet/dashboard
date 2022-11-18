#!/usr/bin/env bash

COUNT=`curl --compressed -s "https://api.gather.town/api/getRoomInfo?room=0v6GlxIbLfBeki85%5CDEPROMEET+12th" | jq -r ".roomCount"` 

echo $COUNT
