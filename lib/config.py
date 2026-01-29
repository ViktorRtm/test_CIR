from datetime import datetime

datetime_format = "%Y-%m-%dT%H:%M:%S"
time_format = "%H:%M:%S"
_print=print
def print(*args, **kw):
    _print(f"[{datetime.now().strftime(datetime_format)}]" ,*args, **kw)