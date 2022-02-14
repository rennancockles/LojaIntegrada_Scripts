from datetime import timedelta


def add_util_days(start_date, n_days):
    response_date = start_date
    delta = timedelta(days=1)
    qtd_util_days = 0

    while qtd_util_days < n_days:
        response_date += delta
        if response_date.weekday() not in (5, 6):
            qtd_util_days += 1

    return response_date
