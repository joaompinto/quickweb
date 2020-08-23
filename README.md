# QuickWeb

QuickWeb is a Python Web Application Server based on the production-proved [CherryPy](https://cherrypy.org/) Web Framework extended with developer friendly features:

## Features
- Custom static content folders (any folder containing a `.static` file)
- Automatic path based routing for templates and controllers, e.g.:
  - /about.html available as /about
  - /submit.py available as /submit
- Zero code Jinja2 template rendering for .html files, that can:
  - Use data from YAML files (file.yaml -> file.html)
  - Use HTTP specific data e.g. {{ session  }}
- Zero code Markdown files rendering
- Low code Python controllers
- Integrated HTTP functional Testing
- Reload on code changes


## Installing
You should be able to use quickweb on both Windows Linux or Mac, if you are on Windows you must install [Python](doc/Windows/Python.md) .


Install quickweb using pip:
```sh
pip install quickweb
```
If the installation is succesful the `quickweb` command will be available, it will allow you to manage quickweb applications from the command line.

## Getting Started
### Creating your first application
Create your first quickweb app using a bootstrap based template:
```sh
quickweb create my-web-app bootstrap-navbar-fixed-top
```
You will get a _my-web-app_ directory containing a quickweb sample app using the [Bootstrap]((https://www.google.com)) library.

### Changing the application content
Check the application directory using your preferred HTML/CSS/JavaScript editor/IDE, edit the the content from the `webroot` directory as desired.

### Starting the application
You made some changes and want to test the application, you can run it with:

```sh
quickweb run my-web-app
```

A CherryPy based web server is started using port 8080 on your local system. You can check your application by browsing to http://localhost:8080. If you later change some of the YAML/HTML/CSS/JS, you can check the changes by refreshing the corresponding page on your browser.

### Deploying to a cloud platform
When your application is ready for public access you can deploy it to a cloud platform, it has been tested with the following providers:
- Heroku Cloud Application Platform (deploy with: git push heroku master)
- IBM Bluemix (deploy with: cf push appname)
- Other CloudFoundry based provider (deploy with: cf push appname)

It should be able to run from other [Cloud Foundry](https://www.cloudfoundry.org) based providers.

NOTES:
 * Check the cloud provider documentation for the web app detailed setup instructions
   - Use the instructions for python web applications setup/deployment
 * The level of support for python based apps will depend on your provider, check it's documentation for details



## Contributing
Check the [Contributing Guide](docs/CONTRIBUTING.md).

Maintained By
-------------

* João Pinto for the [Open Pipe](//github.com/OpenPipe) initiative
