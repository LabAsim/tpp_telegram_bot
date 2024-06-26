# A Telegram bot for TPP and other news sites
A simple Telegram Bot for TPP and other greek news sites.

The bot is hosted on [fly.io](https://fly.io/) and the scraping script on [Apify](https://apify.com/).

### Add it on Telegram! [Click here](https://t.me/TppgrBot)!

## Table of Contents

*   [Installation](#Installation)
*   [fly.io](#Flyio)
*   [Docker](#Docker)
*   [Roadmap](#Roadmap)
*   [Documentation](#Documentation)
*   [Donate](#donate)
*   [License](#license)

## Installation
Run `pip install -r requirements.txt` to install the dependencies.


* Create a .py file:  `saved_tokens.py` which must contain the API keys as constants:
`TOKEN_TELEGRAM_BOT`, `TOKEN_TELEGRAM_BOT_TEST`, `TOKEN_APIFY`

* If you don't want to hard code the tokens into `saved_tokens.py`,
you can set the tokens to environmental variables named as the constants above.
In this case, do not create the `saved_tokens.py` at all.

*   If you want to run the test bot, run `python main.py --test True --dbpass yourpass` (default is `False`).


## Fly.io
Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)

Open a powershell and type:

*   `cd <path to your bot directory>`
*   ``flyctl auth login``
*   `fly launch`
*   `fly deploy` (use deploy to update the app if you have already launched it once)

## Docker

Build the image

``docker build --tag tppbotapp --file <path to the directory>``

Run the bot locally:

``docker run -d tppbotapp``

## Roadmap

* [X]  Integrate [**APSchedule 3.10.4**](https://github.com/agronholm/apscheduler)

* [X]  Migrate to [Aiogram 3.X](https://github.com/aiogram/aiogram)

* [X] Allow scheduled news scraping


* [ _**Ongoing**_ ] User Guide

## Documentation

You can see the documentation [here](https://labasim.github.io/tpp_telegram_bot/).

The documentation is also available from within the application, just send `/help` to
the bot.

## Donate

Do not forget to donate monthly to [ThePressProject team](https://community.thepressproject.gr/?lang=en).
Recurrent monthly donation/funding is the only way for a truly independent journalism to exist.

## License

ThePressProject Trademark, name and all of its content belong to the ThePressProject team.
The same applies to the other news sites.
The 3rd party packages have their own licenses.
All the code written by me is released under the MIT license.
