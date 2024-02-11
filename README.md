# tpp_telegram_bot
A simple Telegram Bot for TPP and other greek news sites.

The bot is hosted in [fly.io](https://fly.io/) and the scraping script in [Apify](https://apify.com/).

Add it in Telegram! [Click here](https://t.me/TppgrBot)!

## Table of Contents

*   [Installation](#Installation)
*   [Docker](#Docker)
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


### Fly.io
Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)

Open a powershell and type:

*   `cd <path to your bot directory>`
*   ``flyctl auth login``
*   `fly launch`
*   `fly deploy` (use deploy to update the app if you have already launched it once)

# Docker

Build the image

``docker build --tag tppbotapp --file <path to the directory>``

Run the bot locally:

``docker run -d tppbotapp``

# Roadmap

* [X]  integrate **APSchedule**

* [ _**ongoing**_ ] Migrate to Aiogram 3.X



## Donate

Do not forget to donate monthly to [ThePressProject team](https://community.thepressproject.gr/?lang=en).
Recurrent monthly donation/funding is the only way for a truly independent journalism to exist.

## License

ThePressProject Trademark, name and all of its content belong to the ThePressProject team.
The same applies to the other news sites.
The 3rd party packages have their own licenses.
All the code written by me is released under the MIT license.
