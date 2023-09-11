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
* `config.py` which must contain `PROXY_URL_PYTHONANYWHERE = "http://proxy.server:3128"`

*   If you want to run the test bot, run `python main.py --debug True` (default is `False`).

### Pythonanywhere
Upload the files in pythonanywhere, open a console and run sequently
* `cd telegram_bot`
* `source venv/bin/activate` (activate the virtual environment)
* `python -m main`


### Fly.io
Install [flyctl](#https://fly.io/docs/hands-on/install-flyctl/)

Open a powershell and type:

*   `cd <path to your bot directory>`
*   ``flyctl auth login``
*   `fly launch`
*   `fly deploy`

# Docker

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
