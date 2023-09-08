# tpp_telegram_bot
A simple Telegram Bot for the TPP .

The bot is hosted in [fly.io](https://fly.io/) or [pythonanywhere](https://www.pythonanywhere.com/) and the scraping script in [Apify](https://apify.com/).

## Table of Contents

*   [Installation](#Installation)
  * [Docker](#Docker)
*   [Donate](#donate)
*   [License](#license)

## Installation
Run `pip install -r requirements.txt` to install the dependencies.

Create two .py files: 
*   `saved_tokens.py` which must contain the API keys as constants: 
`TOKEN_TELEGRAM_BOT`, `TOKEN_TELEGRAM_BOT_TEST`, `TOKEN_APIFY` 
* `config.py` which contains `DEBUG` and`PROXY_URL_PYTHONANYWHERE = "http://proxy.server:3128"`

Upload the files in pythonanywhere, open a console and run sequently 
* `cd telegram_bot` 
* `python -m main`

The `DEBUG=True` allows the test bot to be run locally. 
In the hosted version `DEBUG` must be `False`.

## Docker

Build the image

``docker build --tag tppbotapp --file <path to the directory>``

Run the bot locally:

``docker run -d tppbotapp``


## Donate

Do not forget to donate monthly to [ThePressProject team](https://community.thepressproject.gr/?lang=en). Recurrent monthly donation/funding is the only way for a truly independent journalism to exist.

## License

ThePressProject Trademark, name and all of its content belong to the ThePressProject team.
The 3rd party packages have their own licenses.
All the code written by me is released under the MIT license.