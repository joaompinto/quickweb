QuickWeb Application Development Guidelines
===========================================

Requirements
-------------

In order to develop a web application with `QuickWeb`, know-how with the following topics is recommended:

**Essentials:**

    HTML - Defines a web page fundamental structure

**Standard:**

    CSS - Defines the page layout and elements properties (themes)

HTML and CSS are the fundamental technology for web presentation.

**Advanced:**

    JS (JavaScript) - Application code that will run on the web browser
    Python - Application code that  will run on the web server


QuickWeb Application Structure
------------------------------
app-directory/

    webroot/
        index.html - the application main web page
        /mypage/ - Any subdirectory containing an index.html is a web page (http://site/mypage)
    libs/
        E python packages that may be required by the application
    template/
        Content that can be bed used from any location on you webroot
