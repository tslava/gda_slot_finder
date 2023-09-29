import asyncio
import json
import random
import time
from datetime import datetime
from typing import List

import requests
import telegram

from settings import GOOGLE_TABLE_ID_FOR_CITIZENSHIP_DATA
from utils import write_to_google_sheet

# Telegram Bot Configuration
bot_token = 'REDACTED_BOT_TOKEN'
chat_id = CHAT_ID
bot = telegram.Bot(token=bot_token)

# 1 взрослый, przyjmowanie wniosków paszportowych
# url = 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/rest/schedule/branches/' \
#       '1cf1e3e60eeb96dae2bb572487249bd48cc5bed0024960eaee0c893ce4918569/dates;' \
#       'servicePublicId=4fe2df1ac02036b7096beb9b80b8e0e8924c3c282eb992fc83b5a3977ddd20b1;' \
#       'customSlotLength=10'

# składanie wniosków i dokumentacji do wniosków...
url = 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/rest/schedule/branches/' \
      '1cf1e3e60eeb96dae2bb572487249bd48cc5bed0024960eaee0c893ce4918569/dates;' \
      'servicePublicId=2c5251d564aaf0b09c2a39d69cf7ed4cb1e142ab3a501b4b688e1e7c2d80b8e0;' \
      'customSlotLength=40'
# [{"date":"2023-06-02"},{"date":"2023-06-15"}]

# +1 ребенок
url_1 = 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/rest/schedule/branches/' \
        '1cf1e3e60eeb96dae2bb572487249bd48cc5bed0024960eaee0c893ce4918569/dates;' \
        'servicePublicId=4fe2df1ac02036b7096beb9b80b8e0e8924c3c282eb992fc83b5a3977ddd20b1;' \
        'customSlotLength=15'

# +2 ребенка
url_2 = 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/rest/schedule/branches/' \
        '1cf1e3e60eeb96dae2bb572487249bd48cc5bed0024960eaee0c893ce4918569/dates;' \
        'servicePublicId=4fe2df1ac02036b7096beb9b80b8e0e8924c3c282eb992fc83b5a3977ddd20b1;' \
        'customSlotLength=20'

time_slots = 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/rest/schedule/branches/' \
             '1cf1e3e60eeb96dae2bb572487249bd48cc5bed0024960eaee0c893ce4918569/dates/{date}/times;' \
             'servicePublicId=4fe2df1ac02036b7096beb9b80b8e0e8924c3c282eb992fc83b5a3977ddd20b1;' \
             'customSlotLength=10'

# składanie wniosków i dokumentacji do wniosków... - время
time_slots_2 = 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/rest/schedule/branches/' \
               '1cf1e3e60eeb96dae2bb572487249bd48cc5bed0024960eaee0c893ce4918569/dates/{date}/times;' \
               'servicePublicId=2c5251d564aaf0b09c2a39d69cf7ed4cb1e142ab3a501b4b688e1e7c2d80b8e0;' \
               'customSlotLength=40'

'''response example
[{"date":"2023-06-15","time":"09:10"},{"date":"2023-06-15","time":"10:20"},{"date":"2023-06-15","time":"10:30"},{"date":"2023-06-15","time":"10:40"},{"date":"2023-06-15","time":"10:50"},{"date":"2023-06-15","time":"11:10"},{"date":"2023-06-15","time":"11:20"},{"date":"2023-06-15","time":"11:30"},{"date":"2023-06-15","time":"11:40"},{"date":"2023-06-15","time":"11:50"},{"date":"2023-06-15","time":"12:00"},{"date":"2023-06-15","time":"12:10"},{"date":"2023-06-15","time":"12:20"},{"date":"2023-06-15","time":"12:30"},{"date":"2023-06-15","time":"12:40"},{"date":"2023-06-15","time":"12:50"},{"date":"2023-06-15","time":"13:00"},{"date":"2023-06-15","time":"13:10"},{"date":"2023-06-15","time":"13:20"},{"date":"2023-06-15","time":"13:30"}]'''

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
        'Referer': 'https://rezerwacja.gdansk.uw.gov.pl:8445/qmaticwebbooking/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
    }

    return res


async def format_time_slots(slots: str) -> List[str]:
    # [{"date":"2023-06-15","time":"09:10"},{"date":"2023-06-15","time":"10:20"}]
    time_slots = json.loads(slots)
    return [slot["time"] for slot in time_slots]


async def monitor_slots():
    request_counter = 0
    while True:
        if request_counter % 12 == 0:
            message = f"Raport: zrobiłem już {request_counter} zapytań"
            await bot.send_message(chat_id=chat_id, text=message)

        response = requests.get(url, headers=get_request_headers(), verify=False)
        request_counter += 1
        free_time_slots_found = response.text != '[]'

        # test_text = '[{"date":"2023-06-01"},{"date":"2023-06-14"}]'
        # free_time_slots_found = True

        if free_time_slots_found:
            # await bot.send_message(chat_id=chat_id, text=f'Znalazłem wolne terminy: raw response: {response.text}')
            append_to_sheet = []

            print('Free time slots available! Visit the website now.')
            result = {}
            slots = json.loads(response.text)
            now = datetime.now()

            for slot in slots:
                time_response = requests.get(time_slots_2.format(date=slot["date"]), headers=get_request_headers(),
                                             verify=False)
                if time_response.text != '[]':
                    slot_times = await format_time_slots(time_response.text)
                    result[slot["date"]] = slot_times

                    append_to_sheet.append(dict(
                        found_at=now,
                        date=slot["date"],
                        slots=slot_times,
                    ))
                time.sleep(5)  # seconds

            slots_str = ""
            for date, times in result.items():
                time_string = ' '.join(times)
                slots_str += f"{date}: {time_string}\n"

            message = f'Znalazłem wolne terminy!\n' \
                      f'{slots_str}'

            await bot.send_message(chat_id=chat_id, text=message)
            if append_to_sheet:
                write_to_google_sheet(data=append_to_sheet, table_doc_id=GOOGLE_TABLE_ID_FOR_CITIZENSHIP_DATA)

        minutes = 5
        time.sleep(minutes * 60)  # seconds


if __name__ == '__main__':
    asyncio.run(monitor_slots())
