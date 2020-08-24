# Mutual TLS
Mutual TLS is an authentication method which allows an https server to request an SSL certificate from an https client. This certificate can be required or optional, the server validates that the certificate is authentic «signed by a trusted CA» before passing the identity information to the the application layer.

When set to _optional_, the application may return different replies depending on wether the client is authenticated or not. Setting to _required_ will force all non authenticated requests to be rejected before reaching any application handler.

In order to use Mutual TLS authorization in quickweb, you must set the `SSL_VERIFY_CLIENT_CERT` environment variable to either `required` or `optional`. The variable `SSL_CERTIFICATE_CHAIN` can be set to the file containing the CA chain used for the client certificate validation.
