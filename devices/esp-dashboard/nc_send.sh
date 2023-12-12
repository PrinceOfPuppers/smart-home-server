#!/bin/bash
echo -n "$2" | netcat -u "$1" 6832
