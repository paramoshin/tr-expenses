from __future__ import annotations
from typing import *

import datetime
import requests


EXCH_RATES_BASE_URL = "https://api.exchangeratesapi.io/history?start_at={start_date}&end_at={end_date}&base=TRY&symbols=RUB"


def str_to_num(s: str) -> float:
    try:
        num = float(s.strip().replace(" ", "").replace(",", "."))
        return num
    except Exception as e:
        raise ValueError(f"Wrong string, args={s}")


class ExchApiNotResponding(Exception):
    pass


def date_generator(from_date: datetime.date, to_date: datetime.date) -> Iterator[datetime.date]:
    while from_date <= to_date:
        yield from_date
        from_date = from_date + datetime.timedelta(days=1)


def get_closest_date(for_date: datetime.date, dates: List[datetime.date]) -> datetime.date:
    min_diff_idx = 0
    if dates:
        min_diff = abs((dates[min_diff_idx] - for_date).days)
    if len(dates) >= 2:
        for i in range(1, len(dates)):
            diff = abs((dates[i] - for_date).days)
            if diff < min_diff:
                min_diff = diff
                min_diff_idx = i
    return dates[min_diff_idx]


def get_exchange_rates(start_date: str, end_date: str) -> Dict[str, float]:
    r = requests.get(EXCH_RATES_BASE_URL.format(start_date=start_date, end_date=end_date))
    if r.status_code != 200:
        raise ExchApiNotResponding
    data = r.json()["rates"]
    result = {date: rate["RUB"] for date, rate in data.items()}

    result_dates = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in result.keys()]

    date_gen = date_generator(
        datetime.datetime.strptime(start_date, "%Y-%m-%d").date(),
        datetime.datetime.strptime(end_date, "%Y-%m-%d").date(),
    )

    for date in date_gen:
        if date.strftime("%Y-%m-%d") not in result:
            closest_date = get_closest_date(date, result_dates)
            result[date.strftime("%Y-%m-%d")] = result[closest_date.strftime("%Y-%m-%d")]

    return result

