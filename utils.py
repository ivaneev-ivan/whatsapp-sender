import datetime


def logger_print(message: str, sep=None) -> None:
    date = datetime.datetime.now()
    end = "\n" if sep is None else sep
    print(f"{'[' + date.strftime('%H:%M:%S') + ']' if message not in ['empty', 'sent'] else ''} {message}", end=end)
