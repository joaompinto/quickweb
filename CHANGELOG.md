# ChangeLog

## v1.7.2

* Removed obsolete application.py

## v1.7.1

* Use python:latest for the Docker image

## v1.7.0

* Added environ jinja filter
* Added composed controller (.html and .py with render())

## v1.6.1

* Add Client SSL support (env: SSL_VERIFY_CLIENT_CERT)

## v1.6.0

* Use setuptools_scm for versioning
* Automate release using github versions
* Added documentation for the SSL support


## v1.5.0

* Add SSL support (env: SSL_PRIVATE_KEY, SSL_PRIVATE_KEY, SSL_CERTIFICATE_CHAIN)

## v1.4.1

* Fix app hot reloading on Windows

## v1.4.0

* Set scheme to https when FORCE_HTTPS env is set

## v1.3.2

* Disable sessions by default, can be enabled via boot script


## v1.3.1

* Reload boot/tools when they are changed

## v1.3.0

* Load cherrypy tools from app_dir/tools
* Load modules on app start from app_dir/boot

## v1.2.8

* Set lang to 'en' when hostname has no dot

## v1.2.7

* Make session("key") available on templates

## v1.2.6

* Add controller.render()

## v1.2.5

* Provide environment variables for templates on "env"
* Add support for CORS using CORS_DOMAIN

## v1.2.4

* support variables injection on template render()

## v1.2.3

* reload web server when modules in the lib dir are updated

## v1.2.2

* load modules from application lib/ dir

## v1.2.1

* fix get_domain() with localhost (thanks to Oana Apostol for reporting)

## v1.2.0

* added lang support

## v1.1.0

* added support for dbsupport.py within app dir

## v1.0.1

* Update to python3

## v1.0.0
