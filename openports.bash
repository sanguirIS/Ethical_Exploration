#!/bin/bash

target="192.168.1.100"

for port in {1..65535}; do
    (echo > /dev/tcp/$target/$port) >/dev/null 2>&1 && echo "Port $port is open"
done