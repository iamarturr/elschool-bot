# Elschool VK bot


FILES STRUCTURE
------------

Files and directories in the project:

      eschool/             simple "OOP" elschool api
      handlers/            handlers for bot
      pkg/                 html and css for drawing of school performance
      config.py            config (¯\_(ツ)_/¯)
      converter_html.py    drawing of school performance
      database.db          database (¯\_(ツ)_/¯)
      elschool_top.py      rating rendering by school progress
      main.py              loading bot
      notification.py      notice of new assessment
      requirements.txt     requirements (¯\_(ツ)_/¯)
      start bot.bat        starter bot
      start server.bat     starter server


INSTALLATION
------------
First you need install project and requirements

     git clone https://github.com/iamarturr/elschool-bot.git
     cd elschool-bot
     pip3 install -r requirements.txt

Secondly download [**wkhtmltopdf**](https://wkhtmltopdf.org/downloads.html "https://wkhtmltopdf.org/downloads.html") and add to path bin folder

Thirdly download [**Microsoft Visual C++**](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170 "https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170")


## Configure

1. Set token group in config.py.
2. Set your vk link in config.py.

## Run
     python main.py
     python converter_html.py

or 
* start bot.bat
* start server.bat


## Links
* Elschool (API, HTML, CSS, etc...): https://elschool.ru
* Creator bot: https://github.com/iamarturr
