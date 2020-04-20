#!/bin/bash

# Function to check if a file exists
file_exists() {
  if [ -e "$1" ]; then
    return 0
  else
    return 1
  fi
}

# Check if the rootCA.key file exists before creating it
if file_exists "rootCA.key"; then
  echo "rootCA.key already exists."
else
  openssl genrsa -out rootCA.key 4096
fi

# Check if the rootCA.pem file exists before creating it
if file_exists "rootCA.pem"; then
  echo "rootCA.pem already exists."
else
  openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.pem -subj '/C=US/ST=CA/O=Shatilov, Inc./CN=shatilov.localhost'
fi

# Server certificate creation
if file_exists "server.localhost.key" && file_exists "server.localhost.csr" && file_exists "server.localhost.crt"; then
  echo "Server certificate files already exist."
else
  openssl req -new -nodes -newkey rsa:2048 -keyout server.localhost.key -out server.localhost.csr -config server.openssl.conf
  openssl x509 -req -in server.localhost.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.localhost.crt -days 365 -sha256 -extfile server.openssl.conf -extensions req_ext
fi

# Client certificate creation
if file_exists "client.localhost.key" && file_exists "client.localhost.csr" && file_exists "client.localhost.crt"; then
  echo "Client certificate files already exist."
else
  openssl req -new -nodes -newkey rsa:2048 -keyout client.localhost.key -out client.localhost.csr -config client.openssl.conf
  openssl x509 -req -in client.localhost.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out client.localhost.crt -days 365 -sha256 -extfile client.openssl.conf -extensions req_ext
fi
