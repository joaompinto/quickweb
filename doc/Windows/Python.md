# Install Python + QuickWeb on Windows
This page will guide you on how to install Python and QuickWeb on Windows.

1. Download Python 2.7 from https://www.python.org/downloads/

2. Install it using the .previously downloaded .msi file:

    ![Installing Python 1](Python_Install_1.png "Installing Python 1")


3. Install to the default install folder:

    ![Installing Python 2](Python_Install_2.png "Installing Python 2")

4. **Enable the "Add python.ext to PATH"** at the bottom of the options:

    ![Installing Python 3](Python_Install_3.png "Installing Python 3")

    ![Installing Python 4](Python_Install_4.png "Installing Python 4")

5.  Open a command prompt, install quickweb with the command:

    `pip install quickweb`

6. List the available QuickWeb templates, with the command:

    `quickweb templates`

 7. Create your application using one of the templates using the command:

    `quickweb create my-web-app bootstrap-navbar-fixed-top`

8.  Run your web application using the command:

    `quickweb run my-web-app`

9.  Check it with your  browser, should be available at http://127.0.0.1:8080 .


