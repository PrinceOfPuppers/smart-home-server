#!/bin/bash

def_host=localhost
def_port=6831

HOST=${2:-$def_host}
PORT=${3:-$def_port}

echo -n "$1" | netcat --wait=1 -u $HOST $PORT
