import datetime


def logger_print(message: str, sep=None) -> None:
    date = datetime.datetime.now()
    print(f"{'[' + date.strftime('%H:%M:%S') + ']' if sep is None else ''} {message}", sep="\n" if sep is None else sep)
