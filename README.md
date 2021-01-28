# Plopkoek Discord Bots

This repository is a collection of discord bots for the plopkoek discord server.

First install the dependencies
`pip install -r requirements.txt`

make sure to use at least python 3.7 and preferably use a venv

To run bots use `python -m api.manager <bot A> <bot B> ...`
e.g. (`python -m api.manager quote plopkoek`)

Current supported bots are:

-   quote: Provides a quotebot
-   plopkoek: Provides a bot that handles an imaginary plopkoek currency
-   echo: Purely for basic testing purposes, echoes all chat messages

Bot code can be found in `cogs/`, bot configuration should be done in `/config`

## Configuration

Remove the .sample from each config file and fill in all relevant fields
