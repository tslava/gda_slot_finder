import asyncio
import json
import random
import time
from datetime import datetime
from typing import List

import requests
import telegram

from settings import (
    CITIZENSHIP_DATES_URL,
    CITIZENSHIP_TIMES_URL,
    GOOGLE_TABLE_ID_CITIZENSHIP,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID_CITIZENSHIP,
)
from utils import write_to_google_sheet

# Telegram Bot Configuration
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.43',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
]


def get_request_headers():
    res = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
    }

    return res


async def format_time_slots(slots: str) -> List[str]:
    time_slots = json.loads(slots)
    return [slot["time"] for slot in time_slots]


async def monitor_slots():
    request_counter = 0
    previous_slots: str = ''
    while True:
        if request_counter == 0:
            message = f"Startuję OBYWATELSTWO skanner"
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID_CITIZENSHIP, text=message)

        response = requests.get(CITIZENSHIP_DATES_URL, headers=get_request_headers(), verify=False)
        request_counter += 1
        free_time_slots_found = response.text != '[]'

        if free_time_slots_found:
            append_to_sheet = []

            print('Free time slots available! Visit the website now.')
            result = {}
            slots = json.loads(response.text)
            now = datetime.now()

            for slot in slots:
                time_response = requests.get(
                    CITIZENSHIP_TIMES_URL.format(date=slot["date"]),
                    headers=get_request_headers(),
                    verify=False
                )
                if time_response.text != '[]':
                    slot_times = await format_time_slots(time_response.text)
                    result[slot["date"]] = slot_times

                    append_to_sheet.append(dict(
                        found_at=now,
                        date=slot["date"],
                        slots=slot_times,
                    ))
                time.sleep(5)

            slots_str = ""
            for date, times in result.items():
                time_string = ' '.join(times)
                slots_str += f"{date}: {time_string}\n"

            if slots_str != previous_slots:
                message = f'OBYWATELSTWO: Znalazłem wolne terminy!\n' \
                          f'{slots_str}'
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID_CITIZENSHIP, text=message)
                previous_slots = slots_str
            else:
                print('Slots not changed')

            if append_to_sheet:
                write_to_google_sheet(data=append_to_sheet, table_doc_id=GOOGLE_TABLE_ID_CITIZENSHIP)
        else:
            print(f'No OBYWATELSTWO free time slots found, date reqs count: {request_counter}')
            now = datetime.now()
            print(f"Current time: {now}")

        minutes = 5
        time.sleep(minutes * 60)


if __name__ == '__main__':
    asyncio.run(monitor_slots())
