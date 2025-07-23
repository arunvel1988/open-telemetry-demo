#!/bin/bash

# Ask for IP address
read -p "Enter target IP address (e.g. 127.0.0.1): " TARGET_IP

# Ask for port number
read -p "Enter target port (e.g. 5000): " TARGET_PORT

# Number of requests to send
read -p "Enter number of requests to send: " REQUEST_COUNT

echo "Sending $REQUEST_COUNT requests to http://$TARGET_IP:$TARGET_PORT ..."

for i in $(seq 1 $REQUEST_COUNT)
do
  # Send GET request and print response status code only
  STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$TARGET_IP:$TARGET_PORT/)
  echo "Request #$i -> Status Code: $STATUS_CODE"
  
  # Sleep 1 second between requests (adjust if needed)
  sleep 1
done

echo "Done sending requests."
