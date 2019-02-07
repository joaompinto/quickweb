# Multiple apps using NGINX and Docker
This deployment pattner allows you to run multiple quickweb apps on a single host, keeping container based resources segregation using docker. NGINX will be running as a reverse proxy in the docker host, it will be responsible for the logging, because we don't want them at the container level, it is also expected to provide some performance gain by managing the end client http connections.

## Setup Your QuickWeb App For Docker
On your development system, prepare your quickweb application for Docker with:
```sh
quickweb setup-docker-deployment your-app-directory
```

## Install NGINX and Docker
For the sake of simplicity this intructions assume you will be using a CentOS7 for your server system.

As root on your system's terminal:

```sh
yum install epel-release
yum install docker nginx git
systemctl enable docker
systemctl start docker
systemctl enable nginx
```

## Build and Run The Docker Image
Get the source for your application, for example, from GitHub:
```bash
git clone https://github.com/your_app_git_repo
```

Go into your application directory and build and run the app:
```bash
docker build -t my-quickweb-app .   # Build the image
docker run -d --restart=always -e PORT=8080 -p 8080:8080 my-quickweb-app  # Run in background
curl -I http://localhost:8080   # Test, should return HTTP/1.1 200 OK
```


## Setup NGINX
We will setup a NGINX virtual host to work as a reverse proxy for the app.
```bash
# Disable the default server config
sed -i "/80 default_server;/d" /etc/nginx/nginx.conf
```

Create a file /etc/nginx/conf.d/my-quickweb-app.conf with the content from [nginx-myapp-proxy.conf](nginx-myapp-proxy.conf), adjust the name and port if needed.

Test the configuration and start the nginx service:
```bash
nginx -t && systemctl start nginx
```
Check that you get the expected app content:
```bash
curl http://localhost:80
```

## Setup a free SSL certificate
This instructions with use the "Let's Encrypt" service. Let's Encrypt is a Certificate Authority (CA) that provides an easy way to obtain and install free TLS/SSL certificates.

Install the certification install robot utility (certbot)
```bash
yum install certbot python-certbot-nginx
certbot --nginx -d your-app-hostname
```

"Let's Encrypt" certificates are only valid for 90 days, you must setup the certificate auto-renewal on crontab:
```bash
crontab -e
# Add the following line to the crontab:
15 3 * * * /usr/bin/certbot renew --quiet
```

