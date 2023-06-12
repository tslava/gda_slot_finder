import asyncio
import json
import random
import time
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

import requests
import telegram

from settings import GOOGLE_TABLE_ID_FOR_GET_VNZ_DATA
from utils import write_to_google_sheet

# Telegram Bot Configuration
bot_token = 'REDACTED_BOT_TOKEN'
chat_id = CHAT_ID
bot = telegram.Bot(token=bot_token)

langs = ["pl", "ru", "en"]

url_dates_base = "https://kolejkagdansk.ajhmedia.pl/admin/API/date/5/307/{lang}"
url_times_base = "https://kolejkagdansk.ajhmedia.pl/admin/API/time/5/45/{date}"  # date format: 2023-09-22

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.43',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
]


def get_request_headers():
    request_headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
    }

    return request_headers


async def is_free_time_slots(dates: List[str], days: int) -> Optional[List[str]]:
    today = datetime.now().date()
    x_date = today + timedelta(days=days)
    less_than_x = [date for date in dates if datetime.strptime(date, "%d/%m/%Y").date() < x_date]
    res = less_than_x if less_than_x else None

    return res


async def format_time_slots(data: list) -> str:
    time_slots = []
    for entry in data:
        time = entry["time"]
        time_slots.append(f"{time[:5]}")
        # time_slots.append(f"{time[:5]} - {slots}")
    result = " ".join(time_slots)

    return result


async def monitor_slots():
    request_counter = 0
    while True:
        if request_counter % 5 == 0:
            if request_counter == 0:
                message = f"Startuję VNZ skanner"
            else:
                message = f"Raport: zrobiłem już {request_counter} zapytań VNZ"
            await bot.send_message(chat_id=chat_id, text=message)

        url_dates = url_dates_base.format(lang=random.choice(langs))
        response_dates_raw = requests.get(url_dates, headers=get_request_headers(), verify=False)
        request_counter += 1

        try:
            response_dates = json.loads(response_dates_raw.text)
        except json.decoder.JSONDecodeError:
            message = f"json.decoder.JSONDecodeError. Response was: {response_dates_raw}"
            print(message)
            await bot.send_message(chat_id=chat_id, text=message)
            continue
        else:
            dates_raw = response_dates["DATES"]
            days_period = 90
            free_time_slots = await is_free_time_slots(days=days_period, dates=dates_raw)

            if free_time_slots:
                slots_str = ""
                append_to_sheet = []
                now = datetime.now()

                free_time_slots = free_time_slots[:5]  # изменить если надо больше дат где есть свободные слоты

                for date in free_time_slots:
                    # date format = 22/09/2023 => 2023-09-22
                    time.sleep(5)
                    print('Free time slots available! Visit the website now.')

                    date_obj = datetime.strptime(date, "%d/%m/%Y")
                    transformed_date = date_obj.strftime("%Y-%m-%d")
                    url_times = url_times_base.format(date=transformed_date)

                    try:
                        response_times_raw = requests.get(url_times, headers=get_request_headers(), verify=False)
                    except requests.exceptions.ConnectionError:
                        print("ConnectionError...continue")
                        continue

                    response_times = json.loads(response_times_raw.text)

                    times = response_times["TIMES"]
                    if times:
                        response_times_formatted = await format_time_slots(times)
                        slots_str += f"{transformed_date}: {response_times_formatted}\n"

                        append_to_sheet.append(dict(
                            found_at=now,
                            date=transformed_date,
                            slots=response_times_formatted,
                        ))

                message = f'Znalazłem wolne terminy VNZ w ciągu {days_period} dni!\n' \
                          f'Uzupełnienie lub odbiór dokumentów:\n' \
                          f'{slots_str}'

                await bot.send_message(chat_id=chat_id, text=message)
                write_to_google_sheet(data=append_to_sheet, table_doc_id=GOOGLE_TABLE_ID_FOR_GET_VNZ_DATA)

                print(f"date req count: {request_counter}")

        minutes = 10
        time.sleep(minutes * 60)  # seconds


if __name__ == '__main__':
    asyncio.run(monitor_slots())
