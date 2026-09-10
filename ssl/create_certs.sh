#!/bin/bash
openssl req -config cert-zwift-com.conf -new -x509 -newkey rsa:2048 -nodes -keyout key-zwift-com.pem -days 3650 -out cert-zwift-com.pem
openssl x509 -in cert-zwift-com.pem -text -noout
openssl pkcs12 -export -in cert-zwift-com.pem -inkey key-zwift-com.pem -CSP "Microsoft Enhanced RSA and AES Cryptographic Provider" -out cert-zwift-com.p12
