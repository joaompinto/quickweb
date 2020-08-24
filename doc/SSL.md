# SSL

In order to enable SSL before starting the server you must set the following environment varialbles:

- SSL_PRIVATE_KEY           absolute path to the key PEM file
- SSL_CERTIFICATE           absolute path to the certificate PEM file
- SSL_CERTIFICATE_CHAIN     absolute path to the CA chain PEM file

For testing purposes you can generate a self signed certificate:

```sh
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
export SSL_PRIVATE_KEY=$(pwd)/key.pem
export SSL_CERTIFICATE=$(pwd)/cert.pem

quickweb run test-app

# Browse to https://0.0.0.0:8080
```

NOTE: Because it's a self signed certificate, you will need to go over the security settings of your browser and accept it.
