# IPL Flask Project

This project is a Flask-based app for viewing IPL stats, player data, winnings, and daily fixtures.

## Main Entry Point

The main starting file is:

- `server.py`

Run this file to start the Flask server.

## Prerequisites

- Python 3.8+
- `pip`

## Setup

1. (Optional) Create and activate a virtual environment.
2. Install Flask:

```bash
pip install flask
```

## Run the App

From the project root:

```bash
python server.py
```

By default, the app runs in debug mode.

## Available Routes

- `GET /` → Basic hello response
- `GET /hello` → Secondary hello response
- `GET /stats` → Renders `stats.html`
- `GET /playerStats` → Renders `IPLPlayerStats.html`
- `GET /load-points` → Returns placeholder load-points response
- `GET /player_role.json` → Returns data from `players_role.json`
- `GET /winnings.json` → Returns data from `winnings.json`
- `POST /save-winnings` → Saves posted winnings JSON to `winnings.json`
- `GET /today-fixtures` → Returns fixtures from `schedule.json` matching today’s date

## Project Notes

- Templates are under `templates/`.
- JSON and CSV files in the root are used as data sources.
- `server.py` currently uses `app.run(debug=True)` for local development.
