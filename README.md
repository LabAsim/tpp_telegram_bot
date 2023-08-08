# tpp_telegram_bot
A simple Telegram Bot for the TPP .

The bot is hosted in pythonanywhere and the scraping script in Apify.

## Table of Contents

*   [Installation](#Installation)
*   [Donate](#donate)
*   [License](#license)

## Installation
Run `pip install -r requirements.txt` to install the dependencies.

Create a py file named `saved_tokens.py` which must contain the API keys as constants: 
`TOKEN_TELEGRAM_BOT`, `TOKEN_TELEGRAM_BOT_TEST`, `TOKEN_APIFY`.

Upload the files in pythonanywhere, open a console and run `cd telegram_bot` and
`python -m main`

The `DEBUG=True` allows the test bot to be run locally.

## Donate

Do not forget to donate monthly to [ThePressProject team](https://community.thepressproject.gr/?lang=en). Recurrent monthly donation/funding is the only way for a truly independent journalism to exist.

## License

ThePressProject Trademark, name and all of its content belong to the ThePressProject team.
The 3rd party packages have their own licenses.
All the code written by me is released under the MIT license.