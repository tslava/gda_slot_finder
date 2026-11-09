# GDA Slot Finder

**Get a Telegram ping the moment an appointment opens at the Pomeranian Voivodeship Office in Gdańsk.** Two small monitors poll the office's online booking system and report new slots for:

- submitting a **Polish citizenship** application;
- collecting a **residence card** (*karta pobytu*, "VNZ" in the code).

Slots there are scarce and get taken within minutes, so polling beats refreshing the page by hand. It only reads the public schedule and never books anything for you.

**Stack:** Python · requests · python-telegram-bot · Google Sheets API (optional log) · Docker · Poetry

## Features

- **Citizenship Service Monitor** (`obyw-wniosek.py`): Monitors available slots for document submission services
- **VNZ Service Monitor** (`vnz-odbior-karty.py`): Monitors available slots for VNZ document completion/retrieval services
- **Telegram Notifications**: Instant alerts when new appointment slots are found
- **Google Sheets Logging**: Records all found slots with timestamps for historical tracking

## Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management
- Telegram Bot Token (create via [@BotFather](https://t.me/botfather))
- Google Cloud Service Account with Sheets API access

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tslava/gda_slot_finder.git
   cd gda_slot_finder
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create your environment file:
   ```bash
   cp .env.example .env
   ```

4. Configure the `.env` file with your credentials (see Configuration section below).

5. Place your Google Service Account credentials JSON file in a secure location and update `GOOGLE_CREDENTIALS_FILE_PATH` in `.env`.

## Configuration

Copy `.env.example` to `.env` and fill in your values:

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID_CITIZENSHIP` | Chat ID for citizenship slot notifications |
| `TELEGRAM_CHAT_ID_VNZ` | Chat ID for VNZ slot notifications |
| `GOOGLE_CREDENTIALS_FILE_PATH` | Path to your Google Service Account JSON file |
| `GOOGLE_TABLE_ID_CITIZENSHIP` | Google Sheet ID for logging citizenship slots |
| `GOOGLE_TABLE_ID_VNZ` | Google Sheet ID for logging VNZ slots |
| `CITIZENSHIP_DATES_URL` | API URL for fetching citizenship appointment dates |
| `CITIZENSHIP_TIMES_URL` | API URL for fetching citizenship time slots |
| `VNZ_DATES_URL_BASE` | Base API URL for fetching VNZ dates |
| `VNZ_TIMES_URL_BASE` | Base API URL for fetching VNZ time slots |

### Getting a Telegram Chat ID

1. Create a group or channel in Telegram
2. Add your bot to the group
3. Send a message in the group
4. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Find the chat ID in the response

### Setting up Google Sheets

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API
3. Create a Service Account and download the JSON credentials
4. Create Google Sheets for logging and share them with the service account email
5. Copy the Sheet IDs from the URLs

## Usage

### Running Locally

```bash
# Run citizenship slot monitor
poetry run python src/obyw-wniosek.py

# Run VNZ slot monitor
poetry run python src/vnz-odbior-karty.py
```

### Running with Docker

Build the image:
```bash
docker build -t gda-slot-finder .
```

Run with environment file:
```bash
docker run --env-file .env gda-slot-finder
```

Or pass environment variables directly:
```bash
docker run -e TELEGRAM_BOT_TOKEN=... -e TELEGRAM_CHAT_ID_CITIZENSHIP=... gda-slot-finder
```

To run the VNZ monitor instead of citizenship:
```bash
docker run --env-file .env --entrypoint poetry gda-slot-finder run python src/vnz-odbior-karty.py
```

## Project Structure

```
gda_slot_finder/
├── src/
│   ├── obyw-wniosek.py      # Citizenship slot monitor
│   ├── vnz-odbior-karty.py  # VNZ slot monitor
│   ├── settings.py          # Configuration loader
│   └── utils.py             # Google Sheets utilities
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── Dockerfile               # Docker configuration
├── pyproject.toml           # Poetry dependencies
└── README.md                # This file
```

## How It Works

1. The monitors poll government booking APIs at regular intervals (5 minutes for citizenship, 1 minute for VNZ)
2. When available dates are found, it fetches the available time slots for each date
3. New slots are compared against previously found slots to avoid duplicate notifications
4. Notifications are sent to configured Telegram chats
5. All findings are logged to Google Sheets with timestamps

## License

[MIT](LICENSE)

---

Built by [Wiaczeslaw Cyunczyk](https://cyunczyk.dev)
