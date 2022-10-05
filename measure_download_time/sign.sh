#!/bin/bash

if [ $# -lt 2 ]; then
  echo 1>&2 "$0: Add path to private key and app author's certificate as params"
  exit 2
fi

PRIVATE_KEY=$1
APP_AUTHOR_CERT=$2
base64 manifest.json --wrap=0 > manifest.json.base64
openssl dgst -sha256 -sign $PRIVATE_KEY -out manifest.json.base64.sign.sha256 manifest.json.base64
base64 manifest.json.base64.sign.sha256 --wrap=0 > manifest.json.base64.sign.sha256.base64
base64 $2 --wrap=0 > author.crt.pem.base64
