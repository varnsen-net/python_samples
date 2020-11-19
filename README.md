This repository contains a sample of Python scripts I've written.

# garybot
Garybot is an Internet Relay Chat (IRC) bot with a variety of quality-of-life and entertainment functions.

## Quality of life functions
* **YouTube** — Parses any YouTube links in user messages and fetches video information through the YouTube API. Sends a message to the channel containing the video title, uploader, duration, views, and likes.
* **Twitter** — Parses any Twitter links in user messages and fetches the tweet through the Twitter API. Sends a message to the channel containing the user, date, and tweet text.

## Casino Games
Users can play one of three casino games in a channel designated by the bot admin. Each new player receives a starting balance that is updated each time the user plays a game.
* **Coin Flips** Users can wager fake money on coin flips. The user supplies a wager and a side selection. The bot flips a digital coin, returns the result, calculates the user's earnings, and updates the user's balance.
* **Video Poker** Users can wager fake money on video poker. The user supplies a wager, then the bot deals the user 5 cards. The user then supplies a list of cards to hold, and the bot deals the final hand and returns the results.
* **Blackjack** Users can wager fake money on blackjack. The user supplies a wager, and the bot deals the user a hand.

# ps_maker_crop.py
This script automates the creation of publication-quality figures. The user inputs a list of galaxy IDs, and the script queries a database of Hubble Space Telesacope images, downloads the corresponding data cubes, then outputs a set of images center-cropped on the primary galaxy.

# sf_calculator.py
This simple script uses the Kennicutt–Schmidt law to calculate and plot a galaxy's total star formation rate as a function of time based on that galaxy's initial gas density.

# sig1_sSFR_4panel_plot.py
This script creates a publication-quality plot of high-redshift galaxies with respect to two parameters: star-formation rate, and the mass-density within the galaxy's central kiloparsec. It outputs a plot with four panels, each panel corresponding to one of four redshift bins.
